// ==========================================================================
// FACT KNOWLEDGE LAYER // SYNTHETIX 3D COMMAND CONTROLLER
// High-performance controller with 3D Interactable Force Graph & HUD Drawer
// ==========================================================================

let currentDataset = 'dynamic';
let allFacts = [];
let allRelationships = [];
let allDocuments = [];
let activeRelFilter = 'ALL';
let displayedFactsCount = 50;
let filteredFactsList = [];

// 3D Knowledge Graph State
let graph3DInstance = null;
let isAutoRotating = false;
let rawGraphData = { nodes: [], edges: [] };

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initDropzone();
    fetchStatus();
    loadDatasetShowcase(currentDataset);

    window.addEventListener('resize', handleWindowResize);
});

// ==========================================================================
// NAVIGATION HANDLING (RepoWhisper Command Tabs)
// ==========================================================================
function initNavigation() {
    const tabs = document.querySelectorAll('.command-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetPaneId = tab.getAttribute('data-tab');
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            const targetPane = document.getElementById(targetPaneId);
            if (targetPane) targetPane.classList.add('active');

            if (targetPaneId === 'graph-tab') {
                setTimeout(initKnowledgeGraph, 80);
            }
        });
    });
}

// ==========================================================================
// SYSTEM STATUS & KPI REFRESH
// ==========================================================================
async function fetchStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        
        const statusEl = document.getElementById('system-status-text');
        if (statusEl) {
            statusEl.innerText = `SYSTEM ONLINE // ${data.provider.toUpperCase()} (${data.facts_count} FACTS)`;
        }
        
        const factsBadge = document.getElementById('facts-count-badge');
        if (factsBadge) factsBadge.innerText = data.facts_count;

        const relsBadge = document.getElementById('rels-count-badge');
        if (relsBadge) relsBadge.innerText = data.relationships_count;

        fetchDocuments();
        fetchFacts();
        fetchRelationships();
    } catch (err) {
        console.error('Status fetch error:', err);
    }
}

// ==========================================================================
// DATASET SELECTION & QUICK ACTIONS
// ==========================================================================
async function loadDataset(name) {
    currentDataset = name;
    const switcher = document.getElementById('dataset-switcher');
    if (switcher) switcher.value = name;

    showToast(`INITIATING INGESTION FOR [${name.toUpperCase()}]...`);

    try {
        const res = await fetch(`/api/load-dataset?dataset_name=${encodeURIComponent(name)}`, { method: 'POST' });
        const data = await res.json();
        showToast(`INGESTED ${data.details.documents_ingested} PDFS // EXTRACTED ${data.details.total_facts} GROUNDED FACTS!`);
        fetchStatus();
        loadDatasetShowcase(name);
        
        // Refresh 3D Graph
        if (graph3DInstance) {
            initKnowledgeGraph();
        }
    } catch (err) {
        showToast('INGESTION FAILURE: ' + err.message);
    }
}

function switchDatasetShowcase(val) {
    currentDataset = val;
    loadDatasetShowcase(val);
}

// ==========================================================================
// FOUR CASES SHOWCASE RENDERING
// ==========================================================================
async function loadDatasetShowcase(datasetName) {
    const container = document.getElementById('cases-cards-wrapper');
    if (!container) return;

    container.innerHTML = `
        <div class="cyber-loading">
            <div class="scanner-line"></div>
            ANALYZING GROUNDED EVIDENCE & CLASSIFYING FOUR CASES [${datasetName.toUpperCase()}]...
        </div>
    `;

    try {
        const res = await fetch(`/api/four-cases?dataset=${encodeURIComponent(datasetName)}`);
        const data = await res.json();

        container.innerHTML = `
            <!-- Case 1: Corroboration -->
            <div class="case-card" style="border-left: 6px solid var(--cyber-emerald);">
                <div class="case-card-header">
                    <div class="case-title">
                        <span>🤝</span> [CASE 01 // CROSS-DOC CORROBORATION]: ${data.case_1_corroboration.title}
                    </div>
                    <span class="case-badge-pill badge-corroborated">CORROBORATED (CONFIDENCE 1.0)</span>
                </div>
                <div class="case-grid">
                    ${data.case_1_corroboration.evidence_sources.map(src => `
                        <div class="evidence-box">
                            <div class="evidence-header">
                                <span class="doc-tag">${src.document}</span>
                                <span class="page-chip">PAGE ${src.page}</span>
                            </div>
                            <div class="evidence-quote">"${src.quote}"</div>
                            <div class="text-dim text-sm">${src.context}</div>
                        </div>
                    `).join('')}
                </div>
                <div class="reasoning-box">
                    <div class="reasoning-title">
                        <span>🧠</span> SYSTEM RECONCILIATION LOGIC
                    </div>
                    <p class="reasoning-text">${data.case_1_corroboration.system_reasoning}</p>
                </div>
            </div>

            <!-- Case 2: Genuine Contradiction -->
            <div class="case-card" style="border-left: 6px solid var(--cyber-rose);">
                <div class="case-card-header">
                    <div class="case-title">
                        <span>⚡</span> [CASE 02 // GENUINE CONTRADICTION]: ${data.case_2_contradiction.title}
                    </div>
                    <span class="case-badge-pill badge-contradiction">DIRECT CONFLICT DETECTED</span>
                </div>
                <div class="case-grid">
                    ${data.case_2_contradiction.evidence_sources.map(src => `
                        <div class="evidence-box">
                            <div class="evidence-header">
                                <span class="doc-tag">${src.document}</span>
                                <span class="page-chip">PAGE ${src.page}</span>
                            </div>
                            <div class="evidence-quote" style="border-left-color: var(--cyber-rose);">"${src.quote}"</div>
                            <div class="text-dim text-sm">${src.context}</div>
                        </div>
                    `).join('')}
                </div>
                <div class="reasoning-box">
                    <div class="reasoning-title" style="color: var(--cyber-rose);">
                        <span>⚡</span> CONFLICT AUDIT TRACE
                    </div>
                    <p class="reasoning-text">${data.case_2_contradiction.system_reasoning}</p>
                </div>
            </div>

            <!-- Case 3: Apparent Contradiction Explained -->
            <div class="case-card" style="border-left: 6px solid var(--cyber-amber);">
                <div class="case-card-header">
                    <div class="case-title">
                        <span>🔍</span> [CASE 03 // APPARENT CONTRADICTION]: ${data.case_3_apparent_contradiction_explained.title}
                    </div>
                    <span class="case-badge-pill badge-apparent">TEMPORALLY / CONTEXTUALLY EXPLAINED</span>
                </div>
                <div class="case-grid">
                    ${data.case_3_apparent_contradiction_explained.evidence_sources.map(src => `
                        <div class="evidence-box">
                            <div class="evidence-header">
                                <span class="doc-tag">${src.document}</span>
                                <span class="page-chip">PAGE ${src.page}</span>
                            </div>
                            <div class="evidence-quote" style="border-left-color: var(--cyber-amber);">"${src.quote}"</div>
                            <div class="text-dim text-sm">${src.temporal_context || ''} // Scope: ${src.scope || 'Consolidated'}</div>
                        </div>
                    `).join('')}
                </div>
                <div class="reasoning-box" style="margin-bottom:10px;">
                    <div class="reasoning-title" style="color: var(--cyber-amber);">
                        <span>📐</span> MULTI-DIMENSIONAL CONTEXT RESOLUTION
                    </div>
                    <div style="font-size:0.92rem; color:var(--text-primary); line-height:1.7;">
                        ${Object.entries(data.case_3_apparent_contradiction_explained.context_resolution || {}).map(([k, v]) => `
                            <div><strong style="color:var(--cyber-cyan);">${k.replace('_', ' ').toUpperCase()}:</strong> ${v}</div>
                        `).join('')}
                    </div>
                </div>
                <div class="reasoning-box">
                    <div class="reasoning-title">
                        <span>🧠</span> RECONCILIATION RESOLUTION ANALYSIS
                    </div>
                    <p class="reasoning-text">${data.case_3_apparent_contradiction_explained.system_reasoning}</p>
                </div>
            </div>

            <!-- Case 4: Extraction/Reasoning Failure & Remediation -->
            <div class="case-card" style="border-left: 6px solid var(--cyber-primary);">
                <div class="case-card-header">
                    <div class="case-title">
                        <span>🛡️</span> [CASE 04 // EXTRACTION FAILURE & REMEDIATION]: ${data.case_4_failure_and_remediation.failure_title}
                    </div>
                    <span class="case-badge-pill badge-failure">FAILURE RECOVERY & MITIGATION</span>
                </div>
                <div class="evidence-box">
                    <div class="evidence-header">
                        <span class="doc-tag">${data.case_4_failure_and_remediation.document_name}</span>
                        <span class="page-chip">PAGE ${data.case_4_failure_and_remediation.page_number} // ${data.case_4_failure_and_remediation.failure_type}</span>
                    </div>
                    <div class="evidence-quote" style="border-left-color: var(--cyber-primary);">
                        RAW UNSTRUCTURED STRING: "${data.case_4_failure_and_remediation.raw_text_snippet}"
                    </div>
                    <div style="font-size:0.92rem; color:var(--cyber-rose); margin-top:6px;">
                        <strong>⚠️ PROBLEMATIC EXTRACTION:</strong> ${data.case_4_failure_and_remediation.problematic_extraction}
                    </div>
                </div>
                <div class="reasoning-box">
                    <div class="reasoning-title" style="color: var(--cyber-primary);">
                        <span>🔬</span> ROOT CAUSE & ARCHITECTURAL MITIGATION
                    </div>
                    <p class="reasoning-text" style="margin-bottom:8px;">
                        <strong style="color:var(--text-pure);">ROOT CAUSE:</strong> ${data.case_4_failure_and_remediation.root_cause}
                    </p>
                    <p class="reasoning-text" style="margin-bottom:8px;">
                        <strong style="color:var(--text-pure);">ENGINE HANDLING:</strong> ${data.case_4_failure_and_remediation.handling_and_remediation}
                    </p>
                    <p class="reasoning-text" style="color: var(--cyber-emerald);">
                        <strong>✅ SANITIZED OUTPUT:</strong> ${data.case_4_failure_and_remediation.fixed_or_mitigated_output}
                    </p>
                </div>
            </div>
        `;
    } catch (err) {
        container.innerHTML = `<div class="cyber-loading" style="color:var(--cyber-rose);">ERROR LOADING SHOWCASE: ${err.message}</div>`;
    }
}

// ==========================================================================
// FACT INVENTORY RENDERING (High-Performance Chunked DOM)
// ==========================================================================
async function fetchFacts() {
    try {
        const res = await fetch('/api/facts');
        allFacts = await res.json();
        filteredFactsList = allFacts;
        displayedFactsCount = 50;
        renderFactsTable();
        populateDocFilterOptions();
    } catch (err) {
        console.error('Facts error:', err);
    }
}

function renderFactsTable() {
    const tbody = document.getElementById('facts-table-body');
    const footer = document.getElementById('facts-pagination-footer');
    const counterText = document.getElementById('facts-counter-text');
    if (!tbody) return;

    const factsToRender = filteredFactsList.slice(0, displayedFactsCount);

    if (!factsToRender.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state-cell">NO FACTS FOUND MATCHING CURRENT FILTER PARAMETERS.</td></tr>';
        if (footer) footer.style.display = 'none';
        return;
    }

    let html = '';
    for (let i = 0; i < factsToRender.length; i++) {
        const f = factsToRender[i];
        const rawQuote = (f.evidence && f.evidence.verbatim_quote) ? f.evidence.verbatim_quote : '';
        const preview = rawQuote.length > 90 ? rawQuote.substring(0, 90) + '...' : rawQuote;

        html += `
            <tr>
                <td><span class="fact-entity-chip">${escapeHtml(f.entity)}</span></td>
                <td><span class="fact-attr-chip">${escapeHtml(f.attribute)}</span></td>
                <td><span class="fact-val-chip">${escapeHtml(f.raw_value || String(f.value))} ${f.unit ? `<small>(${escapeHtml(f.unit)})</small>` : ''}</span></td>
                <td><span class="text-dim text-sm">${escapeHtml(f.temporal_context || 'N/A')} // ${escapeHtml(f.scope_context || 'Consolidated')}</span></td>
                <td><span class="doc-tag">${escapeHtml(f.document_name)}</span> <span class="page-chip">p. ${f.page_number}</span></td>
                <td><span class="snippet-preview" title="${escapeHtml(rawQuote)}">"${escapeHtml(preview)}"</span></td>
                <td><button class="cyber-btn btn-cyan btn-sm" onclick="openEvidenceModalById('${f.id}')">GROUNDING</button></td>
            </tr>
        `;
    }
    tbody.innerHTML = html;

    if (footer) {
        footer.style.display = 'flex';
        counterText.innerText = `SHOWING ${Math.min(displayedFactsCount, filteredFactsList.length)} OF ${filteredFactsList.length} FACTS`;
    }
}

function loadMoreFacts() {
    displayedFactsCount += 50;
    renderFactsTable();
}

function filterFacts() {
    const q = (document.getElementById('facts-search-input')?.value || '').toLowerCase();
    const doc = (document.getElementById('facts-doc-filter')?.value || '').toLowerCase();
    const type = document.getElementById('facts-type-filter')?.value || '';

    filteredFactsList = allFacts.filter(f => {
        const matchesQ = !q ||
            f.entity.toLowerCase().includes(q) ||
            f.attribute.toLowerCase().includes(q) ||
            String(f.raw_value || f.value).toLowerCase().includes(q) ||
            (f.evidence && f.evidence.verbatim_quote.toLowerCase().includes(q));

        const matchesDoc = !doc || f.document_name.toLowerCase().includes(doc);
        const matchesType = !type || f.fact_type === type;
        return matchesQ && matchesDoc && matchesType;
    });

    displayedFactsCount = 50;
    renderFactsTable();
}

function populateDocFilterOptions() {
    const select = document.getElementById('facts-doc-filter');
    if (!select) return;
    const docs = [...new Set(allFacts.map(f => f.document_name))];
    select.innerHTML = '<option value="">ALL DOCUMENTS</option>' + docs.map(d => `<option value="${d}">${d.toUpperCase()}</option>`).join('');
}

// ==========================================================================
// RELATIONSHIPS MATRIX (Cross-Doc Discrepancies & Corroborations)
// ==========================================================================
async function fetchRelationships() {
    try {
        const res = await fetch('/api/relationships');
        allRelationships = await res.json();
        
        let apparentCount = 0;
        let contradictionCount = 0;
        allRelationships.forEach(r => {
            if (r.relationship_type === 'APPARENT_CONTRADICTION_EXPLAINED') apparentCount++;
            if (r.relationship_type === 'CONTRADICTION') contradictionCount++;
        });

        const appEl = document.getElementById('kpi-apparent-count');
        if (appEl) appEl.innerText = apparentCount;

        const contraEl = document.getElementById('kpi-contradiction-count');
        if (contraEl) contraEl.innerText = contradictionCount;

        renderRelationships(allRelationships);
    } catch (err) {
        console.error('Relationships error:', err);
    }
}

function renderRelationships(rels) {
    const grid = document.getElementById('relationships-grid');
    if (!grid) return;

    const filtered = activeRelFilter === 'ALL' ? rels : rels.filter(r => r.relationship_type === activeRelFilter);

    if (!filtered.length) {
        grid.innerHTML = '<div class="cyber-loading">NO CROSS-DOCUMENT RELATIONSHIPS MATCH FILTER CRITERIA.</div>';
        return;
    }

    grid.innerHTML = filtered.slice(0, 40).map(r => {
        const badgeClass = r.relationship_type === 'CORROBORATED' ? 'badge-corroborated' :
                           r.relationship_type === 'CONTRADICTION' ? 'badge-contradiction' : 'badge-apparent';
        const typeLabel = r.relationship_type === 'CORROBORATED' ? 'CORROBORATION' :
                          r.relationship_type === 'CONTRADICTION' ? 'DIRECT CONTRADICTION' : 'CONTEXT RESOLVED';

        const borderColor = r.relationship_type === 'CORROBORATED' ? 'var(--cyber-emerald)' :
                            r.relationship_type === 'CONTRADICTION' ? 'var(--cyber-rose)' : 'var(--cyber-amber)';

        return `
            <div class="rel-card" style="border-left: 5px solid ${borderColor};">
                <div class="rel-header">
                    <span class="case-badge-pill ${badgeClass}">${typeLabel}</span>
                    <span class="text-dim text-sm">${r.source_fact?.attribute?.toUpperCase() || 'CROSS-MATCH'}</span>
                </div>
                <div class="rel-comparison-view">
                    <div class="evidence-box">
                        <div class="evidence-header">
                            <span class="doc-tag">${r.source_fact?.document_name}</span>
                            <span class="page-chip">p. ${r.source_fact?.page_number}</span>
                        </div>
                        <div class="fact-val">${r.source_fact?.raw_value || r.source_fact?.value}</div>
                        <div class="evidence-quote" style="font-size:0.86rem;">"${r.source_fact?.evidence.verbatim_quote}"</div>
                    </div>
                    <div class="evidence-box">
                        <div class="evidence-header">
                            <span class="doc-tag">${r.target_fact?.document_name}</span>
                            <span class="page-chip">p. ${r.target_fact?.page_number}</span>
                        </div>
                        <div class="fact-val">${r.target_fact?.raw_value || r.target_fact?.value}</div>
                        <div class="evidence-quote" style="font-size:0.86rem;">"${r.target_fact?.evidence.verbatim_quote}"</div>
                    </div>
                </div>
                <div class="reasoning-box">
                    <div class="reasoning-title">
                        <span>💡</span> RECONCILIATION SYNTHESIS
                    </div>
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

// ==========================================================================
// DOCUMENT INVENTORY & RECONCILE ACTIONS
// ==========================================================================
async function fetchDocuments() {
    try {
        const res = await fetch('/api/documents');
        allDocuments = await res.json();
        const list = document.getElementById('ingested-docs-list');
        if (!list) return;

        if (!allDocuments.length) {
            list.innerHTML = '<div class="text-dim text-sm">NO CUSTOM DOCUMENTS IN MEMORY.</div>';
            return;
        }

        list.innerHTML = allDocuments.map(d => `
            <div class="doc-item-card">
                <div>
                    <strong style="color:var(--text-pure); font-size:1.02rem;">${d.filename}</strong>
                    <div class="text-dim text-sm">${d.page_count} PAGES // ${(d.file_size_bytes / (1024*1024)).toFixed(2)} MB</div>
                </div>
                <span class="case-badge-pill badge-apparent">${d.facts_count} FACTS</span>
            </div>
        `).join('');
    } catch (err) {
        console.error('Docs error:', err);
    }
}

async function reconcileAll() {
    showToast('INITIATING DETERMINISTIC CROSS-DOCUMENT RECONCILIATION...');
    try {
        const res = await fetch('/api/reconcile', { method: 'POST' });
        const data = await res.json();
        showToast(data.message.toUpperCase());
        fetchStatus();
    } catch (err) {
        showToast('RECONCILIATION ERROR: ' + err.message);
    }
}

// ==========================================================================
// SEMANTIC COMMAND LINE Q&A
// ==========================================================================
async function executeQuery() {
    const input = document.getElementById('qa-input');
    const q = input?.value?.trim();
    if (!q) return;

    const resContainer = document.getElementById('qa-results-container');
    const ansText = document.getElementById('qa-answer-text');
    const srcList = document.getElementById('qa-sources-list');

    if (resContainer) resContainer.style.display = 'flex';
    if (ansText) ansText.innerText = 'EXECUTING SEMANTIC GRAPH QUERY & SYNTHESIZING VERIFIED CITATIONS...';
    if (srcList) srcList.innerHTML = '';

    try {
        const res = await fetch('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: q })
        });
        const data = await res.json();

        if (ansText) ansText.innerText = data.answer;
        if (srcList && data.supporting_facts && data.supporting_facts.length) {
            srcList.innerHTML = data.supporting_facts.map(f => `
                <div class="evidence-box">
                    <div class="evidence-header">
                        <span class="doc-tag">${f.document_name}</span>
                        <span class="page-chip">PAGE ${f.page_number} // ${f.entity}</span>
                    </div>
                    <div class="evidence-quote">"${f.evidence.verbatim_quote}"</div>
                    <div class="text-dim text-sm">${f.attribute}: <strong style="color:var(--cyber-cyan);">${f.raw_value || f.value}</strong> (${f.temporal_context || 'N/A'})</div>
                </div>
            `).join('');
        }
    } catch (err) {
        if (ansText) ansText.innerText = 'QUERY EXECUTION ERROR: ' + err.message;
    }
}

function setQuery(text) {
    const input = document.getElementById('qa-input');
    if (input) {
        input.value = text;
        executeQuery();
    }
}

// ==========================================================================
// 3D INTERACTABLE KNOWLEDGE GRAPH (RepoWhisper Three.js Engine)
// ==========================================================================
async function initKnowledgeGraph() {
    const container = document.getElementById('graph-3d-canvas');
    if (!container) return;

    try {
        const res = await fetch('/api/graph');
        const data = await res.json();
        rawGraphData = data;

        // Cap graph rendering to top 90 most connected nodes for silky 60fps 3D
        const nodesToRender = data.nodes.slice(0, 90);
        const nodeIds = new Set(nodesToRender.map(n => n.id));

        const formattedNodes = nodesToRender.map(n => {
            const isDoc = n.type === 'document';
            const isEntity = n.type === 'entity';
            return {
                id: n.id,
                label: n.label || n.id,
                type: n.type,
                details: n.details || {},
                val: isDoc ? 18 : (isEntity ? 12 : 7),
                color: isDoc ? '#FFE600' : (isEntity ? '#00E0FF' : '#BD00FF')
            };
        });

        const formattedLinks = data.edges
            .filter(e => nodeIds.has(e.source) && nodeIds.has(e.target))
            .map(e => {
                const rel = e.relationship_type;
                const linkColor = rel === 'CORROBORATED' ? '#10B981' :
                                  rel === 'CONTRADICTION' ? '#F43F5E' :
                                  rel === 'APPARENT_CONTRADICTION_EXPLAINED' ? '#F59E0B' :
                                  'rgba(255, 255, 255, 0.22)';
                return {
                    source: e.source,
                    target: e.target,
                    relationship_type: rel,
                    color: linkColor,
                    width: rel ? 2.5 : 1
                };
            });

        const gData = { nodes: formattedNodes, links: formattedLinks };

        // Clean any previous instances
        container.innerHTML = '';

        if (typeof ForceGraph3D === 'undefined') {
            container.innerHTML = '<div class="cyber-loading" style="color:var(--cyber-rose);">3D ENGINE LOAD FAILED. CHECK INTERNET OR LOCAL BUNDLE.</div>';
            return;
        }

        const width = container.clientWidth || 900;
        const height = container.clientHeight || 550;

        graph3DInstance = ForceGraph3D()(container)
            .width(width)
            .height(height)
            .graphData(gData)
            .backgroundColor('#0B0F19')
            .nodeLabel(n => `[${n.type.toUpperCase()}] ${n.label}`)
            .nodeColor('color')
            .nodeVal('val')
            .nodeResolution(16)
            .linkColor('color')
            .linkWidth('width')
            .linkDirectionalParticles(2)
            .linkDirectionalParticleSpeed(0.006)
            .linkDirectionalParticleWidth(2.5)
            .onNodeClick(handle3DNodeClick);

        // Position camera for optimal overview
        graph3DInstance.cameraPosition({ x: 0, y: 0, z: 280 });

    } catch (err) {
        console.error('3D Graph initialization error:', err);
    }
}

function handle3DNodeClick(node) {
    if (!graph3DInstance || !node) return;

    // Smooth camera fly-to animation targeting clicked node
    const distance = 90;
    const hyp = Math.hypot(node.x, node.y, node.z) || 1;
    const distRatio = 1 + distance / hyp;

    graph3DInstance.cameraPosition(
        { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio + 40 },
        { x: node.x, y: node.y, z: node.z },
        1500
    );

    openNodeInspector(node);
}

function openNodeInspector(node) {
    const drawer = document.getElementById('node-inspector-drawer');
    const badge = document.getElementById('drawer-node-type');
    const title = document.getElementById('drawer-node-title');
    const body = document.getElementById('drawer-node-body');
    if (!drawer || !badge || !title || !body) return;

    badge.innerText = node.type.toUpperCase();
    badge.style.background = node.type === 'document' ? 'var(--cyber-yellow)' :
                             node.type === 'entity' ? 'var(--cyber-cyan)' : 'var(--cyber-primary)';
    badge.style.color = '#000';
    title.innerText = node.label || node.id;

    // Find facts related to this node
    let matchedFacts = [];
    if (node.type === 'document') {
        matchedFacts = allFacts.filter(f => f.document_name.toLowerCase().includes(node.id.toLowerCase()));
    } else if (node.type === 'entity') {
        matchedFacts = allFacts.filter(f => f.entity.toLowerCase() === node.id.toLowerCase());
    } else {
        matchedFacts = allFacts.filter(f => f.id === node.id);
    }

    let factsHtml = '';
    if (matchedFacts.length) {
        factsHtml = matchedFacts.slice(0, 8).map(f => `
            <div class="evidence-box">
                <div class="evidence-header">
                    <span class="doc-tag">${escapeHtml(f.document_name)}</span>
                    <span class="page-chip">PAGE ${f.page_number}</span>
                </div>
                <div style="font-size:1.05rem; font-weight:900; color:var(--cyber-cyan);">${escapeHtml(f.attribute)}: ${escapeHtml(f.raw_value || String(f.value))}</div>
                <div class="evidence-quote" style="font-size:0.88rem;">"${escapeHtml(f.evidence?.verbatim_quote || '')}"</div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
                    <span class="text-dim text-xs">${escapeHtml(f.temporal_context || 'N/A')}</span>
                    <button class="cyber-btn btn-cyan btn-sm" onclick="openEvidenceModalById('${f.id}')">FULL GROUNDING →</button>
                </div>
            </div>
        `).join('');
    } else {
        factsHtml = '<div class="text-dim text-sm">No direct facts attached to this node index.</div>';
    }

    body.innerHTML = `
        <div style="font-size:0.88rem; color:var(--text-muted); border-bottom:1px solid var(--cyber-border); padding-bottom:8px;">
            ASSOCIATED KNOWLEDGE RECORDS (${matchedFacts.length} FOUND)
        </div>
        ${factsHtml}
    `;

    drawer.style.display = 'flex';
}

function closeNodeInspector() {
    const drawer = document.getElementById('node-inspector-drawer');
    if (drawer) drawer.style.display = 'none';
}

function resetGraphCamera() {
    if (graph3DInstance) {
        graph3DInstance.cameraPosition({ x: 0, y: 0, z: 280 }, { x: 0, y: 0, z: 0 }, 1200);
    }
}

function toggleGraphAutoRotate() {
    if (!graph3DInstance) return;
    const btn = document.getElementById('btn-toggle-rotate');
    isAutoRotating = !isAutoRotating;

    const controls = graph3DInstance.controls();
    if (controls) {
        controls.autoRotate = isAutoRotating;
        controls.autoRotateSpeed = 1.2;
    }

    if (btn) {
        btn.innerHTML = isAutoRotating ? '<span>🔄 AUTO-ROTATE: ON</span>' : '<span>🔄 AUTO-ROTATE: OFF</span>';
        btn.className = isAutoRotating ? 'cyber-btn btn-emerald btn-sm' : 'cyber-btn btn-purple btn-sm';
    }
}

function reheatGraphSimulation() {
    if (graph3DInstance) {
        graph3DInstance.d3ReheatSimulation();
        showToast('RE-HEATED 3D FORCE LAYOUT SIMULATION');
    }
}

function handleWindowResize() {
    if (graph3DInstance) {
        const container = document.getElementById('graph-3d-canvas');
        if (container) {
            graph3DInstance.width(container.clientWidth);
            graph3DInstance.height(container.clientHeight);
        }
    }
}

// ==========================================================================
// GROUNDING & PROVENANCE INSPECTION MODAL
// ==========================================================================
function openEvidenceModalById(factId) {
    const fact = allFacts.find(f => f.id === factId);
    if (!fact) return;

    const modal = document.getElementById('evidence-modal');
    const body = document.getElementById('modal-body');
    if (!modal || !body) return;

    body.innerHTML = `
        <div style="margin-bottom:16px; border-bottom:2px solid var(--cyber-border); padding-bottom:12px;">
            <div style="font-size:1.25rem; font-weight:900; color:var(--text-pure);">${escapeHtml(fact.entity)} — ${escapeHtml(fact.attribute)}</div>
            <div style="margin-top:6px; font-size:1.45rem; color:var(--cyber-cyan); font-weight:900;">
                ${escapeHtml(fact.raw_value || String(fact.value))} ${fact.unit ? `<small>(${escapeHtml(fact.unit)})</small>` : ''}
            </div>
        </div>

        <div class="evidence-box" style="margin-bottom:16px;">
            <div class="evidence-header">
                <span class="doc-tag">${escapeHtml(fact.document_name)}</span>
                <span class="page-chip">PHYSICAL PAGE ${fact.page_number}</span>
            </div>
            <div class="evidence-quote" style="font-size:1.05rem; border-left:4px solid var(--cyber-cyan);">
                "${escapeHtml(fact.evidence.verbatim_quote)}"
            </div>
        </div>

        <div class="reasoning-box" style="margin-bottom:16px;">
            <div class="reasoning-title">
                <span>📄</span> VERBATIM SURROUNDING CONTEXT WINDOW
            </div>
            <div style="font-size:0.92rem; font-family:var(--font-mono); color:var(--text-primary); line-height:1.6; background:#000; padding:12px; border:1px solid var(--cyber-border); white-space:pre-wrap;">
${escapeHtml(fact.evidence.context_window || 'Context window captured.')}
            </div>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; font-size:0.86rem; background:var(--cyber-panel-dark); padding:16px; border:2px solid var(--cyber-border);">
            <div><strong style="color:var(--cyber-cyan);">TEMPORAL ANCHOR:</strong> ${escapeHtml(fact.temporal_context || 'Unspecified')}</div>
            <div><strong style="color:var(--cyber-cyan);">ACCOUNTING SCOPE:</strong> ${escapeHtml(fact.scope_context || 'Standard')}</div>
            <div><strong style="color:var(--cyber-primary);">FACT RECORD ID:</strong> <code>${escapeHtml(fact.id)}</code></div>
            <div><strong style="color:var(--cyber-emerald);">EXTRACTION CONFIDENCE:</strong> ${(fact.confidence * 100).toFixed(0)}%</div>
        </div>
    `;

    modal.style.display = 'flex';
}

function closeEvidenceModal() {
    const modal = document.getElementById('evidence-modal');
    if (modal) modal.style.display = 'none';
}

// ==========================================================================
// DRAG AND DROP PDF UPLOAD
// ==========================================================================
function initDropzone() {
    const dropzone = document.getElementById('pdf-dropzone');
    if (!dropzone) return;

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = 'var(--cyber-primary)';
        dropzone.style.background = 'var(--cyber-panel-alt)';
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.style.borderColor = 'var(--cyber-cyan)';
        dropzone.style.background = 'var(--cyber-panel-dark)';
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = 'var(--cyber-cyan)';
        dropzone.style.background = 'var(--cyber-panel-dark)';
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

    if (progBox) progBox.style.display = 'block';
    if (progBar) progBar.style.width = '40%';
    if (progText) progText.innerText = `INGESTING ${fileList.length} PDF(S)...`;

    try {
        const res = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        if (progBar) progBar.style.width = '100%';
        if (progText) progText.innerText = `SUCCESS! INGESTED ${fileList.length} FILE(S).`;
        setTimeout(() => { if (progBox) progBox.style.display = 'none'; }, 2000);
        showToast(`INGESTION COMPLETE: ${fileList.length} FILES ADDED TO KNOWLEDGE LAYER`);
        fetchStatus();
    } catch (err) {
        showToast('UPLOAD FAILED: ' + err.message);
        if (progBox) progBox.style.display = 'none';
    }
}

// ==========================================================================
// TOAST NOTIFICATIONS
// ==========================================================================
function showToast(msg) {
    const hub = document.getElementById('toast-hub');
    if (!hub) return;

    const toast = document.createElement('div');
    toast.className = 'cyber-toast';
    toast.innerText = msg;
    hub.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3200);
}

// Security Helper
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
