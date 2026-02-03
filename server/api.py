import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from termcolor import colored
import uvicorn
import threading

# Path Hack to include root
sys.path.append(os.path.join(os.getcwd(), '..'))
sys.path.append(os.getcwd())

from main import WMCS_Kernel
from server.telemetry import telemetry

from contextlib import asynccontextmanager

# Global Kernel
kernel = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global kernel
    print(colored("[API] Initializing WMCS Kernel...", "magenta"))
    kernel = WMCS_Kernel()
    kernel.load_data()
    print(colored("[API] Kernel Ready.", "green"))
    yield
    print(colored("[API] Shutting down...", "magenta"))

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="WMCS v2.0 API", description="Cognitive Engine Interface", lifespan=lifespan)

# Enable CORS for Dashboard (file:// access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev
    allow_credentials=False, # Must be False if origin is *
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    text: str
    allow_research: bool = True

@app.get("/status")
def status():
    if not kernel: return {"status": "loading"}
    return {
        "status": "online",
        "vectors": kernel.vector_store.count(),
        # "concepts": len(kernel.blocks)
    }

@app.get("/activity")
def get_activity():
    if not kernel: raise HTTPException(500, "Kernel loading")
    if hasattr(kernel, 'status'):
        return {"activity": kernel.status}
    return {"activity": "Idle"}

@app.get("/logs")
def get_logs(since: float = 0):
    """Return logs newer than timestamp."""
    return telemetry.get_logs(since)

@app.post("/query")
def run_query(req: QueryRequest):
    if not kernel: raise HTTPException(500, "Kernel loading")
    
    import time
    start = time.time()
    print(colored(f"[API] Processing Query: '{req.text}' (Research={req.allow_research})", "cyan"))
    
    try:
        # Returns {text: "...", visited_nodes: [...]}
        response = kernel.process_query(req.text, allow_research=req.allow_research)
        
        elapsed = time.time() - start
        print(colored(f"[API] Query Complete in {elapsed:.2f}s", "green"))
        
        # Validation: Ensure response is dict
        if isinstance(response, str):
            return {"text": response, "visited_nodes": []}
        return response
        
    except Exception as e:
        print(colored(f"[API CRASH] {str(e)}", "red"))
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Kernel Crash: {str(e)}")

class VerifyRequest(BaseModel):
    query: str
    response: str

@app.post("/verify")
def run_verification(req: VerifyRequest):
    """
    Asks the 'Smart Verifier' to critique the system's answer.
    """
    if not kernel: raise HTTPException(500, "Kernel loading")
    
    # Lazy Init of Verifier (CLI tools are not always loaded in API)
    # But we can instantiate it here since we have kernel.llm_client
    from system_a_cognitive.meta.verifier import ExternalVerifier
    verifier = ExternalVerifier(kernel.llm_client)
    
    print(colored(f"[API] Verifying: '{req.query}'...", "yellow"))
    report = verifier.verify(req.query, req.response)
    print(colored(f"[API] Verdict: {report.get('status')} (Score: {report.get('score')})", "cyan"))
    
    return report

@app.get("/graph")
def get_graph(limit: int = 500, focus: str = None):
    """
    Returns graph data for 3D visualizer.
    If focus is provided, returns Ego Graph (neighbors).
    Else returns global graph (limited).
    """
    if not kernel: raise HTTPException(500, "Kernel loading")
    
    nodes = []
    links = []
    
    # Simple strategy: Use the ID Map or iterate VectorStore results
    # Since VectorStore is abstract, we rely on kernel.blocks if loaded in RAM
    # OR we query Chroma for random/all items.
    
    # For visualization, we need LINKS. Links are in 'claims' (Object IDs).
    # Since kernel.blocks is populated in 'main.py' load_data line 62...
    # BUT we changed load_data to skip loading if DB is full.
    # SO kernel.blocks might be EMPTY if we are in "Chroma Only" mode.
    # WE MUST FIX THIS. The Visualizer needs the Network Structure.
    
    # Fallback: Query Chroma for 'all' (up to limit)
    # This is tricky with Chroma 0.4.
    # We will use the 'peek' method or 'get'.
    
    # 1. Build Nodes (Safe Block)
    try:
        data = kernel.vector_store.collection.get(limit=limit, include=['metadatas', 'documents'])
        # data['ids'], data['metadatas']
        
        id_set = set()
        
        for i, doc_id in enumerate(data['ids']):
            meta = data['metadatas'][i]
            name = meta.get('name', 'Unknown')
            group = meta.get('group', 0)
            
            nodes.append({
                "id": doc_id,
                "name": name,
                "val": 1, # Size
                "color": "#00ff88" if group==100 else "#ffffff" # Highlight elements
            })
            id_set.add(doc_id)
    except Exception as e:
        print(colored(f"[API ERROR] Node Generation Failed: {e}", "red"))
        return {"nodes": [], "links": [], "error": f"NodeGen: {str(e)}"}

    # 2. Build Links (Riskier Block)
    try:
        # Iterate over loaded blocks to find connections
        if kernel and kernel.blocks:
            for name, block in kernel.blocks.items():
                source_id = f"{block.get('id',{}).get('group',0)},{block.get('id',{}).get('item',0)}"
                
                if source_id not in id_set: continue

                claims = block.get('claims', [])
                facets = block.get('facets', {})
                
                def add_link(target_raw):
                    target_id = None
                    if "->" in target_raw and "(" in target_raw:
                        try:
                            parts = target_raw.split('(')[1].split(')')[0].split(',')
                            if len(parts) >= 2:
                                target_id = f"{parts[0].strip()},{parts[1].strip()}"
                        except: pass
                    
                    if target_id and target_id in id_set:
                        links.append({
                            "source": source_id,
                            "target": target_id,
                            "value": 1
                        })
                
                for c in claims:
                    add_link(str(c.get('object', '')))
                
                if isinstance(facets, dict):
                    for section in facets.values():
                        if isinstance(section, dict):
                            for k, v in section.items():
                                if isinstance(v, list):
                                    for item in v: add_link(str(item))
                                else:
                                    add_link(str(v))

    except Exception as e:
        print(colored(f"[API WARN] Link Generation Failed: {e}", "yellow"))
        # We Do NOT return error here, we just return nodes without links


    return {"nodes": nodes, "links": links}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
