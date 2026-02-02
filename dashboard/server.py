import http.server
import socketserver
import json
import os
import sys

# Configuration
PORT = 8080 # Changed to 8080 to avoid conflicts
ROOT_DIR = os.getcwd() 
DATA_DIR = os.path.join(ROOT_DIR, "data", "concepts")
DASHBOARD_DIR = os.path.join(ROOT_DIR, "dashboard")

class WMCSHandler(http.server.SimpleHTTPRequestHandler):
    """
    Robust Handler: Maps root URLs directly to dashboard/ folder files.
    """
    def do_GET(self):
        print(f"DEBUG: Request for {self.path}")
        
        # 1. API Handling
        if self.path.startswith("/api/"):
            return self.handle_api()

        # 2. Static File Handling (Manual Mapping)
        # Map root requests to dashboard folder
        if self.path == "/" or self.path == "/index.html":
            self.serve_file(os.path.join(DASHBOARD_DIR, "index.html"), "text/html")
        elif self.path == "/style.css":
            self.serve_file(os.path.join(DASHBOARD_DIR, "style.css"), "text/css")
        elif self.path == "/app.js":
            self.serve_file(os.path.join(DASHBOARD_DIR, "app.js"), "application/javascript")
        elif self.path.startswith("/dashboard/"):
            # Fallback for old URL structure, redirect to root
            new_path = self.path.replace("/dashboard/", "/")
            self.send_response(301)
            self.send_header("Location", new_path)
            self.end_headers()
        else:
            # 404 for anything else
            self.send_error(404, "File not found")

    def serve_file(self, local_path, content_type):
        if os.path.exists(local_path):
            self.send_response(200)
            self.send_header('Content-type', content_type)
            # Disable caching to fix "plain UI" issues immediately
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.end_headers()
            with open(local_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            print(f"ERROR: File missing: {local_path}")
            self.send_error(404, "File not found on server")

    def handle_api(self):
        if self.path == "/api/concepts":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            concepts = []
            if os.path.exists(DATA_DIR):
                for f in os.listdir(DATA_DIR):
                    if f.endswith(".json"):
                        try:
                            with open(os.path.join(DATA_DIR, f), 'r', encoding='utf-8') as file:
                                data = json.load(file)
                                concepts.append({
                                    "filename": f,
                                    "name": data.get("name", "Unknown"),
                                    "id": str(data.get("id", "??")),
                                    "group": data.get("id", {}).get("group", 0) if isinstance(data.get("id"), dict) else 0,
                                    "type": data.get("primary_type", "UNKNOWN")
                                })
                        except Exception as e:
                            print(f"Error reading {f}: {e}")
            
            concepts.sort(key=lambda x: (x['group'], x['name']))
            self.wfile.write(json.dumps(concepts).encode())
            
        elif self.path.startswith("/api/concept/"):
            filename = self.path.split("/")[-1]
            filepath = os.path.join(DATA_DIR, filename)
            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Concept not found")
        
        elif self.path == "/api/activity":
            log_path = os.path.join(ROOT_DIR, "data", "logs", "subconscious_events.json")
            if os.path.exists(log_path):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                with open(log_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                # Return empty list if no log yet
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b"[]")
                
        else:
             self.send_error(404, "API endpoint not found")

if __name__ == "__main__":
    print(colored_print := lambda t, c: print(t) )
    try:
        from termcolor import colored
        colored_print = lambda t, c: print(colored(t, c))
    except ImportError: pass

    colored_print(f"\n╔════════════════════════════════════════════╗", "cyan")
    colored_print(f"║   WMCS DASHBOARD SERVER v2.0 (ROBUST)      ║", "cyan")
    colored_print(f"╚════════════════════════════════════════════╝", "cyan")
    print(f" -> URL: http://localhost:{PORT}")
    print("\nPress Ctrl+C to stop.\n")

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), WMCSHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
