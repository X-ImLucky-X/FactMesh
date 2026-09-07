// Fact Knowledge Layer - Frontend Controller
let currentDataset = 'delhivery';
let allFacts = [];
let allRelationships = [];
let allDocuments = [];
let activeRelFilter = 'ALL';

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initDropzone();
    loadDatasetShowcase(currentDataset);
    fetchStatus();
});

// Navigation Handling
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
            const activePane = document.getElementById(targetTab);
            if (activePane) activePane.classList.add('active');

            // Update top bar title
            const tabTitles = {
                'cases-tab': 'Four Cases Showcase',
                'facts-tab': 'Fact Explorer & Provenance',
                'relationships-tab': 'Cross-Document Relationships',
                'graph-tab': 'Interactive Knowledge Graph',
                'query-tab': 'Semantic Intelligence & Q&A',
                'upload-tab': 'Upload & Ingest Documents'
            };
            document.getElementById('page-title').innerText = tabTitles[targetTab] || 'Fact Knowledge Layer';

            if (targetTab === 'graph-tab') {
                initKnowledgeGraph();
            }
        });
    });
}

// Fetch System Status & Ingested Counts
async function fetchStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        document.getElementById('system-status-text').innerText = `Engine: ${data.provider.toUpperCase()} (${data.facts_count} facts)`;
        document.getElementById('facts-count-badge').innerText = data.facts_count;
        document.getElementById('rels-count-badge').innerText = data.relationships_count;

        // Fetch docs
        fetchDocuments();
        fetchFacts();
        fetchRelationships();
    } catch (err) {
        console.error('Error fetching status:', err);
    }
}

// Load Starter Dataset
async function loadDataset(name) {
    currentDataset = name;
    document.getElementById('dataset-switcher').value = name;
    showNotification(`Loading ${name} dataset...`);

    try {
        const res = await fetch(`/api/load-dataset?dataset_name=${encodeURIComponent(name)}`, { method: 'POST' });
        const data = await res.json();
        showNotification(`Ingested ${data.details.documents_ingested} PDFs with ${data.details.total_facts} facts!`);
        fetchStatus();
        loadDatasetShowcase(name);
    } catch (err) {
        alert('Error loading dataset: ' + err.message);
    }
}

function switchDatasetShowcase(val) {
    currentDataset = val;
    loadDatasetShowcase(val);
}

// Load Four Cases Showcase
async function loadDatasetShowcase(datasetName) {
    const container = document.getElementById('cases-cards-wrapper');
    container.innerHTML = '<div class="loading-spinner">Loading showcase cases...</div>';

    try {
        const res = await fetch(`/api/four-cases?dataset=${encodeURIComponent(datasetName)}`);
        const data = await res.json();

        container.innerHTML = `
            <!-- Case 1: Corroboration -->
            <div class="case-card">
                <div class="case-card-header">
                    <div class="case-title">
                        <span>🤝</span> ${data.case_1_corroboration.title}
                    </div>
                    <span class="case-badge-pill badge-corroborated">Corroborated</span>
                </div>
                <div class="case-grid">
                    ${data.case_1_corroboration.evidence_sources.map(src => `
                        <div class="evidence-box">
                            <div class="evidence-header">
                                <span class="doc-tag">${src.document}</span>
                                <span>Page ${src.page}</span>
                            </div>
                            <div class="evidence-quote">"${src.quote}"</div>
                            <div class="text-dim text-sm">${src.context}</div>
                        </div>
                    `).join('')}
                </div>
                <div class="reasoning-box">
                    <div class="reasoning-title">
                        <span>🧠</span> System Semantic Reasoning & Reconciliation
                    </div>
                    <p class="reasoning-text">${data.case_1_corroboration.system_reasoning}</p>
                </div>
            </div>

            <!-- Case 2: Genuine Contradiction -->
            <div class="case-card">
                <div class="case-card-header">
                    <div class="case-title">
                        <span>⚡</span> ${data.case_2_contradiction.title}
                    </div>
                    <span class="case-badge-pill badge-contradiction">Contradiction</span>
                </div>
                <div class="case-grid">
                    ${data.case_2_contradiction.evidence_sources.map(src => `
                        <div class="evidence-box">
                            <div class="evidence-header">
                                <span class="doc-tag">${src.document}</span>
                                <span>Page ${src.page}</span>
                            </div>
                            <div class="evidence-quote">"${src.quote}"</div>
                            <div class="text-dim text-sm">${src.context}</div>
                        </div>
                    `).join('')}
                </div>
                <div class="reasoning-box">
                    <div class="reasoning-title">
                        <span>🧠</span> System Semantic Reasoning & Conflict Detection
                    </div>
                    <p class="reasoning-text">${data.case_2_contradiction.system_reasoning}</p>
                </div>
            </div>

            <!-- Case 3: Apparent Contradiction Explained -->
            <div class="case-card">
                <div class="case-card-header">
                    <div class="case-title">
                        <span>🔍</span> ${data.case_3_apparent_contradiction_explained.title}
                    </div>
                    <span class="case-badge-pill badge-apparent">Contextually Resolved</span>
                </div>
                <div class="case-grid">
                    ${data.case_3_apparent_contradiction_explained.evidence_sources.map(src => `
                        <div class="evidence-box">
                            <div class="evidence-header">
                                <span class="doc-tag">${src.document}</span>
                                <span>Page ${src.page} • ${src.temporal_context || ''}</span>
                            </div>
                            <div class="evidence-quote">"${src.quote}"</div>
                            <div class="text-dim text-sm">Scope: ${src.scope || 'Consolidated'}</div>
                        </div>
                    `).join('')}
                </div>
                <div class="reasoning-box" style="margin-bottom:12px;">
                    <div class="reasoning-title"><span>📐</span> Context Dimension Breakdown</div>
                    <ul style="margin-left:20px; font-size:0.86rem; color:#d1d5db; line-height:1.6;">
                        ${Object.entries(data.case_3_apparent_contradiction_explained.context_resolution || {}).map(([k, v]) => `
                            <li><strong>${k.replace('_', ' ').toUpperCase()}:</strong> ${v}</li>
                        `).join('')}
                    </ul>
                </div>
                <div class="reasoning-box">
                    <div class="reasoning-title">
                        <span>🧠</span> System Multi-Dimensional Reconciliation Logic
                    </div>
                    <p class="reasoning-text">${data.case_3_apparent_contradiction_explained.system_reasoning}</p>
                </div>
            </div>

            <!-- Case 4: Extraction/Reasoning Failure & Remediation -->
            <div class="case-card" style="border-left: 3px solid var(--color-failure);">
                <div class="case-card-header">
                    <div class="case-title">
                        <span>🛡️</span> ${data.case_4_failure_and_remediation.failure_title}
                    </div>
                    <span class="case-badge-pill" style="background:var(--color-failure-bg); color:var(--color-failure); border:1px solid rgba(236,72,153,0.3);">Failure Analysis & Fix</span>
                </div>
                <div class="evidence-box" style="margin-bottom: 16px;">
                    <div class="evidence-header">
                        <span class="doc-tag">${data.case_4_failure_and_remediation.document_name}</span>
                        <span>Page ${data.case_4_failure_and_remediation.page_number} • ${data.case_4_failure_and_remediation.failure_type}</span>
                    </div>
                    <div class="evidence-quote" style="border-left-color: var(--color-failure);">
                        Raw Extraction Snippet: "${data.case_4_failure_and_remediation.raw_text_snippet}"
                    </div>
                    <p style="font-size:0.84rem; color:#fca5a5; margin-top:6px;">
                        <strong>⚠️ Problematic Extraction:</strong> ${data.case_4_failure_and_remediation.problematic_extraction}
                    </p>
                </div>
                <div class="reasoning-box">
                    <div class="reasoning-title" style="color: #f472b6;">
                        <span>🔬</span> Root Cause & Architectural Remediation
                    </div>
                    <p class="reasoning-text" style="margin-bottom:8px;">
                        <strong>Root Cause:</strong> ${data.case_4_failure_and_remediation.root_cause}
                    </p>
                    <p class="reasoning-text" style="margin-bottom:8px;">
                        <strong>Handling & Remediation:</strong> ${data.case_4_failure_and_remediation.handling_and_remediation}
                    </p>
                    <p class="reasoning-text" style="color: #6ee7b7;">
                        <strong>✅ Mitigated Output:</strong> ${data.case_4_failure_and_remediation.fixed_or_mitigated_output}
                    </p>
                </div>
            </div>
        `;
    } catch (err) {
        container.innerHTML = `<div class="text-center text-muted">Error loading showcase: ${err.message}</div>`;
    }
}

// Fetch & Display Facts
async function fetchFacts() {
    try {
        const res = await fetch('/api/facts');
        allFacts = await res.json();
        renderFactsTable(allFacts);
        populateDocFilterOptions();
    } catch (err) {
        console.error('Error fetching facts:', err);
    }
}

function renderFactsTable(facts) {
    const tbody = document.getElementById('facts-table-body');
    if (!facts.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No facts found matching criteria.</td></tr>';
        return;
    }

    tbody.innerHTML = facts.map(f => `
        <tr>
            <td><strong>${f.entity}</strong></td>
            <td>${f.attribute}</td>
            <td><span class="fact-val">${f.raw_value || f.value}</span> ${f.unit ? `<small class="text-dim">(${f.unit})</small>` : ''}</td>
            <td><span class="text-sm">${f.temporal_context || '—'}</span><br><small class="text-dim">${f.scope_context || ''}</small></td>
            <td><span class="doc-tag" title="${f.document_name}">${f.document_name}</span><br><span class="text-dim text-sm">Page ${f.page_number}</span></td>
            <td><span class="text-sm text-dim" style="max-width:240px; display:block; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">"${f.evidence.verbatim_quote}"</span></td>
            <td>
                <button class="btn btn-sm btn-outline" onclick='openEvidenceModal(${JSON.stringify(f).replace(/'/g, "&apos;")})'>
                    View Evidence
                </button>
            </td>
        </tr>
    `).join('');
}

function filterFacts() {
    const q = document.getElementById('facts-search-input').value.toLowerCase();
    const doc = document.getElementById('facts-doc-filter').value.toLowerCase();
    const type = document.getElementById('facts-type-filter').value;

    const filtered = allFacts.filter(f => {
        const matchesQ = !q || f.entity.toLowerCase().includes(q) || f.attribute.toLowerCase().includes(q) || String(f.value).toLowerCase().includes(q) || f.evidence.verbatim_quote.toLowerCase().includes(q);
        const matchesDoc = !doc || f.document_name.toLowerCase().includes(doc);
        const matchesType = !type || f.fact_type === type;
        return matchesQ && matchesDoc && matchesType;
    });

    renderFactsTable(filtered);
}

function populateDocFilterOptions() {
    const select = document.getElementById('facts-doc-filter');
    const docs = [...new Set(allFacts.map(f => f.document_name))];
    select.innerHTML = '<option value="">All Documents</option>' + docs.map(d => `<option value="${d}">${d}</option>`).join('');
}

// Fetch & Display Relationships
async function fetchRelationships() {
    try {
        const res = await fetch('/api/relationships');
        allRelationships = await res.json();
        renderRelationships(allRelationships);
    } catch (err) {
        console.error('Error fetching relationships:', err);
    }
}

function renderRelationships(rels) {
    const grid = document.getElementById('relationships-grid');
    const filtered = activeRelFilter === 'ALL' ? rels : rels.filter(r => r.relationship_type === activeRelFilter);

    if (!filtered.length) {
        grid.innerHTML = '<div class="loading-spinner">No cross-document relationships match this filter.</div>';
        return;
    }

    grid.innerHTML = filtered.map(r => {
        const badgeClass = r.relationship_type === 'CORROBORATED' ? 'badge-corroborated' :
                           r.relationship_type === 'CONTRADICTION' ? 'badge-contradiction' : 'badge-apparent';
        const typeLabel = r.relationship_type === 'CORROBORATED' ? 'Corroboration' :
                          r.relationship_type === 'CONTRADICTION' ? 'Contradiction' : 'Contextually Resolved';

        return `
            <div class="rel-card">
                <div class="rel-header">
                    <span class="case-badge-pill ${badgeClass}">${typeLabel}</span>
                    <span class="text-dim text-sm">${r.source_fact?.attribute || 'Cross-Match'}</span>
                </div>
                <div class="rel-comparison-view">
                    <div class="evidence-box">
                        <div class="evidence-header">
                            <span class="doc-tag">${r.source_fact?.document_name}</span>
                            <span>p. ${r.source_fact?.page_number}</span>
                        </div>
                        <div class="fact-val" style="margin-bottom:4px;">${r.source_fact?.raw_value || r.source_fact?.value}</div>
                        <div class="evidence-quote" style="font-size:0.78rem;">"${r.source_fact?.evidence.verbatim_quote}"</div>
                    </div>
                    <div class="evidence-box">
                        <div class="evidence-header">
                            <span class="doc-tag">${r.target_fact?.document_name}</span>
                            <span>p. ${r.target_fact?.page_number}</span>
                        </div>
                        <div class="fact-val" style="margin-bottom:4px;">${r.target_fact?.raw_value || r.target_fact?.value}</div>
                        <div class="evidence-quote" style="font-size:0.78rem;">"${r.target_fact?.evidence.verbatim_quote}"</div>
                    </div>
                </div>
                <div class="reasoning-box">
                    <div class="reasoning-title"><span>💡</span> Reconciliation Synthesis</div>
                    <p class="reasoning-text" style="white-space: pre-line;">${r.reasoning}</p>
                </div>
            </div>
        `;
    }).join('');
}

function filterRelationships(type, btn) {
    activeRelFilter = type;
    document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
    if (btn) btn.classList.add('active');
    renderRelationships(allRelationships);
}

// Fetch Documents
async function fetchDocuments() {
    try {
        const res = await fetch('/api/documents');
        allDocuments = await res.json();
        const list = document.getElementById('ingested-docs-list');
        if (!allDocuments.length) {
            list.innerHTML = '<div class="text-muted text-sm">No documents in memory yet.</div>';
            return;
        }
        list.innerHTML = allDocuments.map(d => `
            <div class="doc-item-card">
                <div>
                    <strong>${d.filename}</strong>
                    <div class="text-dim text-sm">${d.page_count} pages • ${(d.file_size_bytes / (1024*1024)).toFixed(2)} MB</div>
                </div>
                <span class="badge">${d.facts_count} facts</span>
            </div>
        `).join('');
    } catch (err) {
        console.error('Error fetching docs:', err);
    }
}

// Reconcile Trigger
async function reconcileAll() {
    showNotification('Re-running cross-document reconciliation...');
    try {
        const res = await fetch('/api/reconcile', { method: 'POST' });
        const data = await res.json();
        showNotification(data.message);
        fetchStatus();
    } catch (err) {
        alert('Reconciliation error: ' + err.message);
    }
}

// Q&A Execution
async function executeQuery() {
    const input = document.getElementById('qa-input');
    const q = input.value.trim();
    if (!q) return;

    const resContainer = document.getElementById('qa-results-container');
    const ansText = document.getElementById('qa-answer-text');
    const srcList = document.getElementById('qa-sources-list');

    resContainer.style.display = 'flex';
    ansText.innerText = 'Analyzing knowledge layer and synthesizing cross-document evidence...';
    srcList.innerHTML = '';

    try {
        const res = await fetch('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: q })
        });
        const data = await res.json();

        ansText.innerText = data.answer;
        if (data.supporting_facts && data.supporting_facts.length) {
            srcList.innerHTML = data.supporting_facts.map(f => `
                <div class="evidence-box">
                    <div class="evidence-header">
                        <span class="doc-tag">${f.document_name}</span>
                        <span>Page ${f.page_number} • ${f.entity}</span>
                    </div>
                    <div class="evidence-quote">"${f.evidence.verbatim_quote}"</div>
                    <div class="text-dim text-sm">${f.attribute}: <strong>${f.raw_value || f.value}</strong> (${f.temporal_context || 'N/A'})</div>
                </div>
            `).join('');
        }
    } catch (err) {
        ansText.innerText = 'Error processing query: ' + err.message;
    }
}

function setQuery(text) {
    document.getElementById('qa-input').value = text;
    executeQuery();
}

// Evidence Modal
function openEvidenceModal(fact) {
    const modal = document.getElementById('evidence-modal');
    const body = document.getElementById('modal-body');

    body.innerHTML = `
        <div style="margin-bottom:16px;">
            <h4>${fact.entity} — ${fact.attribute}</h4>
            <div style="margin-top:6px; font-size:1.1rem; color:#60a5fa; font-weight:600;">${fact.raw_value || fact.value} ${fact.unit ? `<small>(${fact.unit})</small>` : ''}</div>
        </div>
        <div class="evidence-box" style="margin-bottom:16px;">
            <div class="evidence-header">
                <span>Exact Source: ${fact.document_name}</span>
                <span>Page: ${fact.page_number}</span>
            </div>
            <div class="evidence-quote" style="font-size:0.95rem;">"${fact.evidence.verbatim_quote}"</div>
        </div>
        <div class="reasoning-box">
            <div class="reasoning-title"><span>📄</span> Surrounding Context Window</div>
            <div class="reasoning-text" style="font-size:0.82rem; font-family:monospace; line-height:1.6;">${fact.evidence.context_window || 'Context window captured.'}</div>
        </div>
        <div style="margin-top:16px; display:grid; grid-template-columns:1fr 1fr; gap:12px; font-size:0.82rem;" class="text-dim">
            <div><strong>Temporal Period:</strong> ${fact.temporal_context || 'Unspecified'}</div>
            <div><strong>Accounting Scope:</strong> ${fact.scope_context || 'Standard'}</div>
            <div><strong>Fact ID:</strong> <code>${fact.id}</code></div>
            <div><strong>Extraction Confidence:</strong> ${(fact.confidence * 100).toFixed(0)}%</div>
        </div>
    `;

    modal.style.display = 'flex';
}

function closeEvidenceModal() {
    document.getElementById('evidence-modal').style.display = 'none';
}

// File Upload & Drag-and-Drop
function initDropzone() {
    const dropzone = document.getElementById('pdf-dropzone');
    dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.style.borderColor = '#3b82f6'; });
    dropzone.addEventListener('dragleave', () => { dropzone.style.borderColor = 'rgba(255,255,255,0.18)'; });
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = 'rgba(255,255,255,0.18)';
        if (e.dataTransfer.files.length) uploadFiles(e.dataTransfer.files);
    });
}

function handleFileSelection(e) {
    if (e.target.files.length) uploadFiles(e.target.files);
}

async function uploadFiles(fileList) {
    const formData = new FormData();
    for (let i = 0; i < fileList.length; i++) {
        formData.append('files', fileList[i]);
    }

    const progBox = document.getElementById('upload-progress-container');
    const progBar = document.getElementById('upload-progress-bar');
    const progText = document.getElementById('upload-progress-text');

    progBox.style.display = 'block';
    progBar.style.width = '40%';
    progText.innerText = `Ingesting ${fileList.length} PDF(s)...`;

    try {
        const res = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        progBar.style.width = '100%';
        progText.innerText = `Complete! Ingested ${fileList.length} files.`;
        setTimeout(() => { progBox.style.display = 'none'; }, 2000);
        fetchStatus();
    } catch (err) {
        alert('Upload failed: ' + err.message);
        progBox.style.display = 'none';
    }
}

// Interactive Knowledge Graph Canvas Simulation
let graphNodes = [];
let graphEdges = [];
let isDragging = false;
let draggedNode = null;
let hoveredNode = null;

async function initKnowledgeGraph() {
    const canvas = document.getElementById('graph-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;

    try {
        const res = await fetch('/api/graph');
        const data = await res.json();

        // Layout nodes in 2D space with force-directed positions
        const w = canvas.width;
        const h = canvas.height;

        graphNodes = data.nodes.map((n, i) => {
            const angle = (i / data.nodes.length) * 2 * Math.PI;
            const radius = n.type === 'document' ? 120 : (n.type === 'entity' ? 200 : 280);
            return {
                ...n,
                x: w/2 + radius * Math.cos(angle) + (Math.random() - 0.5) * 50,
                y: h/2 + radius * Math.sin(angle) + (Math.random() - 0.5) * 50,
                vx: 0,
                vy: 0,
                r: n.type === 'document' ? 16 : (n.type === 'entity' ? 12 : 8),
                color: n.type === 'document' ? '#3b82f6' : (n.type === 'entity' ? '#8b5cf6' : '#10b981')
            };
        });

        graphEdges = data.edges;

        setupCanvasInteractions(canvas);
        requestAnimationFrame(renderGraphLoop);
    } catch (err) {
        console.error('Error loading graph:', err);
    }
}

function renderGraphLoop() {
    const canvas = document.getElementById('graph-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw edges
    ctx.lineWidth = 1;
    for (const e of graphEdges) {
        const src = graphNodes.find(n => n.id === e.source);
        const tgt = graphNodes.find(n => n.id === e.target);
        if (src && tgt) {
            ctx.strokeStyle = e.relationship_type ? '#f59e0b' : 'rgba(255, 255, 255, 0.12)';
            ctx.beginPath();
            ctx.moveTo(src.x, src.y);
            ctx.lineTo(tgt.x, tgt.y);
            ctx.stroke();
        }
    }

    // Draw nodes
    for (const n of graphNodes) {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, 2 * Math.PI);
        ctx.fillStyle = n.color;
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = (hoveredNode && hoveredNode.id === n.id) ? 3 : 1;
        ctx.stroke();

        // Node label
        ctx.fillStyle = '#d1d5db';
        ctx.font = '10px Inter, sans-serif';
        ctx.textAlign = 'center';
        const label = n.label.length > 20 ? n.label.slice(0, 18) + '...' : n.label;
        ctx.fillText(label, n.x, n.y + n.r + 12);
    }
}

function setupCanvasInteractions(canvas) {
    const tooltip = document.getElementById('graph-tooltip');

    canvas.onmousemove = (e) => {
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        hoveredNode = graphNodes.find(n => Math.hypot(n.x - mx, n.y - my) <= n.r + 4);

        if (hoveredNode) {
            tooltip.style.display = 'block';
            tooltip.style.left = `${e.clientX + 12}px`;
            tooltip.style.top = `${e.clientY + 12}px`;
            tooltip.innerHTML = `<strong>${hoveredNode.type.toUpperCase()}:</strong> ${hoveredNode.label}`;
            canvas.style.cursor = 'pointer';
        } else {
            tooltip.style.display = 'none';
            canvas.style.cursor = 'default';
        }

        if (isDragging && draggedNode) {
            draggedNode.x = mx;
            draggedNode.y = my;
            renderGraphLoop();
        }
    };

    canvas.onmousedown = (e) => {
        if (hoveredNode) {
            isDragging = true;
            draggedNode = hoveredNode;
        }
    };

    window.onmouseup = () => {
        isDragging = false;
        draggedNode = null;
    };
}

function showNotification(msg) {
    console.log('[FactLayer Notification]', msg);
}
