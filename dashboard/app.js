const API_BASE = "/api";

// STATE
let allConcepts = [];
let currentConcept = null;

// GROUP DEFINITIONS
const GROUP_MAP = {
    10: "SYSTEM CORE",
    20: "PHYSICAL_OBJ",
    21: "INGESTION",
    30: "ABSTRACT",
    99: "MOCK_DATA"
};

// DOM ELEMENTS
const conceptListEl = document.getElementById('concept-list');
const searchInput = document.getElementById('search-input');
const emptyState = document.getElementById('empty-state');
const detailView = document.getElementById('detail-view');

// INIT
document.addEventListener('DOMContentLoaded', () => {
    fetchConcepts();

    searchInput.addEventListener('input', (e) => {
        renderList(e.target.value);
    });

    // Start Neural Activity Feed
    fetchActivity();
    setInterval(fetchActivity, 2000);
});

async function fetchConcepts() {
    try {
        const res = await fetch(`${API_BASE}/concepts`);
        allConcepts = await res.json();

        document.getElementById('stat-count').textContent = allConcepts.length;
        const groups = new Set(allConcepts.map(c => c.id?.group || 0));
        document.getElementById('stat-groups').textContent = groups.size;

        renderList();
    } catch (err) {
        conceptListEl.innerHTML = `<div class="error">Failed to connect to Neural Link.<br>Is server running?</div>`;
    }
}

function formatID(idObj) {
    if (!idObj) return "[??:??]";
    const g = idObj.group;
    const i = idObj.item;
    const gName = GROUP_MAP[g] || "UNKNOWN";
    return `[${g}:${gName}.${i}]`;
}

function renderList(filter = "") {
    conceptListEl.innerHTML = "";
    const term = filter.toLowerCase();

    allConcepts.forEach(c => {
        if (c.name.toLowerCase().includes(term) || (c.filename && c.filename.includes(term))) {
            const el = document.createElement('div');
            el.className = `concept-item ${currentConcept?.filename === c.filename ? 'active' : ''}`;
            el.onclick = () => loadConcept(c.filename);

            const idStr = formatID(c.id);

            el.innerHTML = `
                <span class="item-name">${c.name}</span>
                <span class="item-meta">${c.type} • <span class="accent">${idStr}</span></span>
            `;
            conceptListEl.appendChild(el);
        }
    });
}

async function loadConcept(filename) {
    try {
        const res = await fetch(`${API_BASE}/concept/${filename}`);
        const data = await res.json();
        currentConcept = { ...data, filename }; // keep filename

        renderDetail(data);
        renderList(searchInput.value); // refresh active state
    } catch (err) {
        console.error(err);
    }
}

function renderDetail(data) {
    emptyState.classList.add('hidden');
    detailView.classList.remove('hidden');

    // Header
    setText('view-name', data.name);
    setText('view-id', formatID(data.id)); // Use new formatter
    setText('view-type', data.primary_type || data.type);
    setText('view-status', data.status || 'PROVISIONAL');
    setText('view-conf-val', `${(data.confidence || 0) * 100}%`);
    document.getElementById('view-conf-bar').style.width = `${(data.confidence || 0) * 100}%`;

    // Surface
    setText('surface-def', data.surface_layer?.definition || "No definition found.");

    const metaList = document.getElementById('surface-meta');
    metaList.innerHTML = "";
    if (data.surface_layer) {
        for (const [k, v] of Object.entries(data.surface_layer)) {
            if (k === 'definition') continue;
            metaList.innerHTML += `<li><span class="data-label">${k}</span> <span>${v}</span></li>`;
        }
    }

    // Deep
    if (data.deep_layer?.mechanism) {
        setText('deep-mech', data.deep_layer.mechanism);
    } else {
        setText('deep-mech', "No mechanism data.");
    }

    document.getElementById('deep-data').textContent = JSON.stringify(data.deep_layer || {}, null, 2);

    // Facets
    const facetsContainer = document.getElementById('facets-container');
    facetsContainer.innerHTML = "";
    if (data.facets) {
        // Handle array format (from prompts v2) OR object format (legacy)
        if (Array.isArray(data.facets)) {
            data.facets.forEach(facet => {
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `<h3>${facet.type}</h3><pre class="code-block">${facet.value}</pre>`;
                facetsContainer.appendChild(card);
            });
        } else {
            for (const [lens, content] of Object.entries(data.facets)) {
                if (Object.keys(content).length === 0) continue;
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `<h3>${lens} LENS</h3><pre class="code-block">${JSON.stringify(content, null, 2)}</pre>`;
                facetsContainer.appendChild(card);
            }
        }
    }

    // Relations
    const relList = document.getElementById('relations-list');
    relList.innerHTML = "";
    if (data.relations && data.relations.length > 0) {
        data.relations.forEach(r => {
            relList.innerHTML += `<li><span class="data-label">${r.relation_type}</span> <span>${r.target}</span></li>`;
        });
    } else {
        relList.innerHTML = "<li>No relations defined.</li>";
    }

    // Raw
    document.getElementById('raw-json').textContent = JSON.stringify(data, null, 2);
}

function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

window.switchTab = (tabName) => {
    // Buttons
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');

    // Panes
    document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
    const pane = document.getElementById(`tab-${tabName}`);
    if (pane) pane.classList.add('active');
};

/* NEURAL ACTIVITY FEED */
async function fetchActivity() {
    try {
        const response = await fetch(`${API_BASE}/activity`);
        if (!response.ok) return;
        const events = await response.json();
        renderActivity(events);
    } catch (e) {
        // Silent fail
    }
}

function renderActivity(events) {
    const list = document.getElementById('activity-list');
    if (!list) return;

    list.innerHTML = '';

    // Events come in chronological order (oldest first). 
    // We render them as is (log style).

    events.forEach(ev => {
        const item = document.createElement('div');
        // Clean type for class
        const typeClass = ev.type.replace(/_/g, '-');
        item.className = `activity-item type-${ev.type}`;

        const date = new Date(ev.timestamp * 1000);
        const timeStr = date.toLocaleTimeString('en-US', { hour12: false });

        // Add detail tooltip logic if needed later
        item.innerHTML = `<span class="timestamp">[${timeStr}]</span> <strong>${ev.type}</strong>: ${ev.message}`;
        list.appendChild(item);
    });

    // Auto scroll to bottom to see latest
    list.scrollTop = list.scrollHeight;
}
