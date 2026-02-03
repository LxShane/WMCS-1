const API_URL = "http://127.0.0.1:8000";
let Graph = null;
let lastLogTime = 0;
let isBusy = false;

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
    initGraph();
    startPolling();

    // Event Listeners
    document.getElementById('send-btn').addEventListener('click', sendQuery);
    document.getElementById('query-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendQuery();
    });
});

// --- GRAPH VISUALIZATION ---
async function initGraph() {
    try {
        const res = await fetch(`${API_URL}/graph?limit=500`);
        const data = await res.json();

        const elem = document.getElementById('3d-graph');
        Graph = ForceGraph3D()
            (elem)
            .graphData(data)
            .nodeLabel('name')
            .nodeAutoColorBy('group')
            .nodeVal('val')
            .linkWidth(1)
            .linkColor(() => '#334155')
            .backgroundColor('rgba(0,0,0,0)') // Transparent
            .showNavInfo(false);

        // Adjust canvas size
        setTimeout(() => {
            if (Graph) Graph.width(elem.clientWidth).height(elem.clientHeight);
        }, 100);

    } catch (e) {
        logToTerminal(`[UI ERROR] Graph Init Failed: ${e.message}`, 'red');
    }
}

// --- TELEMETRY LOOP ---
function startPolling() {
    setInterval(pollLogs, 1500); // 1.5s for logs
    setInterval(pollStatus, 3000); // 3s for stats
}

async function pollLogs() {
    try {
        const res = await fetch(`${API_URL}/logs?since=${lastLogTime}`);
        const logs = await res.json();

        if (logs.length > 0) {
            logs.forEach(entry => {
                logToTerminal(entry.message, entry.color, entry.time_str);
                lastLogTime = entry.timestamp;
            });
        }
    } catch (e) {
        // Silent fail on polling errors to avoid span
    }
}

async function pollStatus() {
    try {
        const res = await fetch(`${API_URL}/status`);
        const data = await res.json();

        document.getElementById('stat-vectors').innerText = data.vectors || "--";
        // Update cache size if available
        if (data.cache_size) {
            document.getElementById('stat-cache').innerText = data.cache_size;
        }
    } catch (e) { }
}

// --- TERMINAL UTILS ---
function logToTerminal(msg, color = 'white', timeStr = null) {
    const term = document.getElementById('terminal');
    const row = document.createElement('div');
    row.className = 'log-entry';

    const ts = document.createElement('span');
    ts.className = 'ts';
    ts.innerText = timeStr || new Date().toLocaleTimeString().split(' ')[0];

    const content = document.createElement('span');
    content.className = `log-msg ${color}`; // Uses CSS classes .cyan, .red etc
    content.innerText = msg;

    row.appendChild(ts);
    row.appendChild(content);

    term.appendChild(row);
    term.scrollTop = term.scrollHeight;

    // Update counter
    const count = term.children.length;
    document.getElementById('log-count').innerText = `${count} events`;
}

// --- CHAT LOGIC ---
async function sendQuery() {
    if (isBusy) return;

    const input = document.getElementById('query-input');
    const text = input.value.trim();
    if (!text) return;

    // UI Update
    addChatMessage(text, 'user');
    input.value = '';
    setBusy(true);

    try {
        const res = await fetch(`${API_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        const data = await res.json();

        if (data.text) {
            addChatMessage(data.text, 'ai');
        } else {
            addChatMessage("Received empty response.", 'ai');
        }

        // Highlight Graph
        if (data.visited_nodes && Graph) {
            highlightNodes(data.visited_nodes);
        }

    } catch (e) {
        addChatMessage(`Error: ${e.message}`, 'ai');
        logToTerminal(`[API ERROR] ${e.message}`, 'red');
    }

    setBusy(false);
}

function addChatMessage(text, role) {
    const hist = document.getElementById('chat-history');
    const div = document.createElement('div');
    div.className = `msg ${role}`;
    div.innerText = text;
    hist.appendChild(div);
    hist.scrollTop = hist.scrollHeight;
}

function setBusy(busy) {
    isBusy = busy;
    const dot = document.getElementById('status-dot');
    const txt = document.getElementById('status-text');
    if (busy) {
        dot.className = 'dot busy';
        txt.innerText = 'PROCESSING';
    } else {
        dot.className = 'dot active';
        txt.innerText = 'SYSTEM ONLINE';
    }
}

// --- GRAPH HIGHLIGHTING ---
function highlightNodes(ids) {
    const { nodes } = Graph.graphData();
    let target = null;

    nodes.forEach(n => {
        if (ids.includes(n.id)) {
            n.color = '#e879f9'; // Magenta
            n.val = 5;
            target = n;
        } else {
            n.color = n.group === 100 ? '#10b981' : '#ffffff'; // Reset
            n.val = 1;
        }
    });

    Graph.graphData({ nodes, links: Graph.graphData().links });

    if (target) {
        const dist = 60;
        Graph.cameraPosition(
            { x: target.x, y: target.y, z: target.z + dist }, // new pos
            target, // lookAt
            2000  // ms
        );
    }
}

function cleanReset() {
    if (confirm("Reset System? This clears RAM.")) {
        // Implement reset endpoint call if needed
        location.reload();
    }
}
