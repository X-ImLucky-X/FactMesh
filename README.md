# 🌌 FactMesh: AI Fact Knowledge Layer & Cross-Document Intelligence

### Automated Evidence Grounding, Reconciliation & 3D Knowledge Command Center
**Hiring Assignment Submission: Superjoin VIT 2026 Engineering Intern**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Three.js](https://img.shields.io/badge/Three.js-3D%20WebGL-black.svg?logo=three.js&logoColor=white)](https://threejs.org/)
[![Repository](https://img.shields.io/badge/GitHub-FactMesh-BD00FF.svg?logo=github&logoColor=white)](https://github.com/X-ImLucky-X/FactMesh)

---

## 🎥 Video Demo

> **Demo Video Link:** **[▶️ Click Here to Watch the Demo Video (≤ 3 minutes)](https://drive.google.com/file/d/1QdPUSitQ0M0e9QFFij_1oAAEx7RJpS3h/view?usp=sharing)**

### Video Coverage (Under 3 Minutes):
1. **0:00 – 0:40 | PDF Ingestion & Real-Time Processing**: Drag-and-drop ingestion of a multi-page PDF into the dashboard; immediate parsing into grounded facts with exact physical page coordinates and verbatim quotes.
2. **0:40 – 1:30 | The Four Required Cases**:
   - **Case 1 (Corroboration)**: Independent verification of MD & CEO designation across distinct filings.
   - **Case 2 (Genuine Contradiction)**: Numerical conflict detected on Restated Loss (`₹4,157.43M` vs `₹415.7M`).
   - **Case 3 (Apparent Contradiction Explained)**: Disentangling 9-month vs 12-month revenue discrepancies through multi-axis context delta.
   - **Case 4 (Failure & Recovery)**: Autonomous detection of legal boilerplate pollution in corporate addresses and confidence-based remediation.
3. **1:30 – 2:20 | 3D Interactive Knowledge Graph**: Orbit navigation, camera flight, dynamic photon particle pulses on corroboration/conflict edges, and sliding node drawer.
4. **2:20 – 3:00 | Unseen Custom PDF Processing**: Ingesting multi-column tabular fact sheets (Infosys / Apple / Tesla) with zero hardcoded schemas or document rules.

---

## 📖 Introduction

> **Stop reading documents in isolation. Start reconciling them.**

Traditional RAG and Knowledge Graph systems treat unstructured documents as flat text chunks, relying on naive vector similarity without understanding whether facts **corroborate, contradict, or evolve over time**.

**FactMesh** is an open-domain, schema-flexible **Fact Knowledge Layer** that extracts grounded facts from multi-document collections, binds them to exact physical page numbers and verbatim quotation snippets, discovers cross-document relationships (corroborations, genuine conflicts, and contextual divergence), and visualizes the resulting factual topology in an interactive **3D WebGL force graph**.

---

## ✨ Key Capabilities

### 🚀 1. Strict Evidence Grounding & Provenance
* Every single extracted fact retains its **1-indexed physical document page coordinate**, **verbatim quotation snippet**, and surrounding bounding sentence context.
* Zero ungrounded claims or hallucinated facts.

### ⚖️ 2. Multi-Dimensional Fact Reconciliation
* **Direct Corroboration**: Identifies agreements across differing institutional filings, even across phrasing and reporting styles.
* **Genuine Contradictions**: Detects conflicting figures for identical metrics and temporal periods (e.g., typos or conflicting institutional forecasts).
* **Apparent Contradictions (Contextually Resolved)**: Disentangles figures that seem to disagree but are reconciled by **time** (FY22 vs FY24), **accounting scope** (Consolidated vs Segment), or **reporting unit** (₹ Cr vs ₹ Mn).
* **Failure Discovery & Remediation**: Surfaces extraction ambiguities (e.g. unparseable legal clauses or table column shifts) and provides algorithmic recovery.

### 🌌 3. Interactive 3D Knowledge Graph
* Visualizes your document universe as a **force-directed 3D knowledge graph** powered by Three.js.
* **3D Orbit Navigation**: Left-click drag to rotate in 3D, right-click to pan, scroll wheel to zoom.
* **Directional Photon Particles**: Animated pulses travel along links (Green for corroborations, Red for contradictions, Amber for contextual resolutions).
* **Smooth Camera Flight**: Clicking any node flies the camera directly to focus on that entity or document.
* **Sliding Node Inspector Drawer**: Inspects all associated facts, page citations, and verbatim evidence.

### 🎨 4. Synthetix Cyberpunk Brutalism UI
* Custom dev command center inspired by **RepoWhisper**:
  - Deep Space Obsidian canvas (`#0B0F19`) with animated retro dot-grid background.
  - Electric Purple (`#BD00FF`) & Bright Cyan (`#00E0FF`) cyber accents.
  - Hard rigid drop shadows (`4px 4px 0px #000`) and tactile button physics.
  - **Large, soothing typography** engineered for high-resolution displays to eliminate eye strain.

### ⚡ 5. 100% Offline Local Engine + Optional LLM Mode
* Runs out-of-the-box in local offline mode without external API keys or network dependencies.
* Seamlessly leverages cloud LLMs (Google Gemini / OpenAI) when API keys are provided in `.env`.

---

## 🧠 Approach

### 1. Architectural Blueprint
```text
       ┌────────────────────────┐
       │   PDF Document Stream  │ (Fact Sheets, Prospectuses, Reports)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │  PyMuPDF Parser & 2D   │  Spatial coordinate grids, font spans,
       │  Vector Table Finder   │  and 2D bounding boxes (page.find_tables)
       └───────────┬────────────┘
                   │
                   ▼
   ┌────────────────────────────────┐
   │     Hybrid Fact Extractor      │  High-precision AST tokenization,
   │  • Deterministic Regex & AST   │  canonical financial metric resolution,
   │  • Normalized Units & Scales   │  and exact page quotation binding
   │  • Exact Page Quote Bounder    │
   └───────────────┬────────────────┘
                   │
                   ▼
   ┌────────────────────────────────┐
   │  Incremental Knowledge Layer   │  Dynamic Entity-Attribute index,
   │  • Entity-Attribute Index      │  provenance citation registry,
   │  • Multi-PDF Graph Topology    │  and cross-document relationship cache
   └───────────────┬────────────────┘
                   │
                   ▼
   ┌────────────────────────────────┐
   │ Cross-Document Reconciliation  │  Pairwise alignment across distinct files:
   │  • Corroboration Engine        │  • Identical facts -> Corroborated
   │  • Contradiction Detector      │  • Conflicting values -> Direct Contradiction
   │  • Multi-Axis Delta Decomposer │  • Reconciled by context -> Apparent Contradiction
   └───────────────┬────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
┌──────────────────┐  ┌──────────────────┐
│  Next-Gen Web UI │  │ FastAPI REST API │
│  3D Force Graph  │  │   /docs Swagger  │
└──────────────────┘  └──────────────────┘
```

### 2. How Facts are Discovered, Grounded, Compared, and Explained
- **The Document Guides the Schema**: The system does not rely on hardcoded company names, predefined SQL schemas, or brittle field dictionaries. The document's textual structure and tables dictate what counts as a fact (e.g. `Revenues`, `Gross Profit`, `Operating Margin`, `Headcount`, `Macro Rates`).
- **Physical Page-Level Evidence Grounding**: Every fact extracted is strictly tied to its physical 1-indexed document page number, verbatim snippet, and bounding text context window. There are zero ungrounded facts.
- **Multi-Axis Context Delta Decomposition**: When two documents present numbers that appear to disagree, the engine decomposes the divergence across four contextual axes:
  1. **Temporal Horizon**: 9-month stub period vs 12-month full audited fiscal year.
  2. **Accounting Scope**: Consolidated group total vs standalone business segment.
  3. **Reporting Units**: ₹ Crore vs US $ Million vs Percentage.
  4. **Reporting Basis / Standards**: Restated vs Unaudited vs IFRS vs Ind AS.

### 3. Important Decisions & Trade-offs
- **High-Speed Deterministic Parser vs Pure LLM Calls**: We prioritized local deterministic extraction (PyMuPDF + AST patterns) as the default engine over sending every page to a cloud LLM. This delivers sub-second fact processing, zero token costs, and 100% mathematical reproducibility with zero hallucination.
- **2D Table Grid Reconstruction**: Multi-column tables in financial statements often stream vertically in naive text extractors. By implementing 2D vector table detection (`page.find_tables()`), we preserve column headers, multi-quarter timelines, and exact metric alignments.
- **WebGL 3D Interactive Force Graph**: Rather than static 2D flowcharts, we built a 3D WebGL knowledge graph (Three.js) with animated photon particle trails. Corroborations glow emerald green, contradictions flash crimson red, and contextually explained facts shine amber.

### 4. AI Tools Used
- **Google Antigravity & Gemini CLI**: Used for architectural scaffolding, iterative pair-programming, and unit verification.
- **Optional Cloud LLM Inference Engine**: Configured with direct adapters for Google Gemini (`gemini-1.5-flash`) and OpenAI (`gpt-4o`) for open-domain unstructured semantic reasoning when API keys are supplied.

---

## 🚀 Setup and Run Instructions

FactMesh is engineered to run **100% locally and offline out-of-the-box** without any paid services or mandatory API keys.

### 1. Prerequisites
- **Python 3.10** or higher
- **Git**

### 2. Clone and Setup Environment
```bash
# Clone the repository
git clone https://github.com/X-ImLucky-X/FactMesh.git
cd FactMesh

# (Recommended) Create and activate a virtual environment
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Start the Web Command Center
```bash
python main.py
```
* **Interactive Web Dashboard**: Open [http://localhost:8000](http://localhost:8000) in your browser.
* **Interactive REST API Docs (Swagger UI)**: Open [http://localhost:8000/docs](http://localhost:8000/docs).

### 4. CLI Usage (Terminal Evaluation)
You can also run fact extraction, dataset loading, and cross-document reasoning entirely from your terminal:
```bash
# Ingest the starter Delhivery dataset
python cli.py load --dataset delhivery

# Display the Four Core Evaluated Cases
python cli.py cases --dataset delhivery

# Ingest any custom PDF(s)
python cli.py ingest path/to/document.pdf

# Ask questions with verified citations
python cli.py query "What was the revenue growth across filings?"
```

### 5. Uploading & Testing Custom Unseen PDFs
1. Open the web UI at `http://localhost:8000`.
2. Drag and drop any PDF into the **Upload PDF** dropzone (e.g. financial fact sheets, annual reports, earnings presentations).
3. Watch the facts counter increment, view citations with page numbers, and inspect the 3D graph in real time.
---

## 🎯 The Four Required Cases (Evaluated & Verified)

### Case 1: Corroboration Across Sources
* **Fact**: Sahil Barua serves as Managing Director and Chief Executive Officer.
* **Source A**: *01-delhivery-drhp.pdf* (Physical Page 84 / Section: Management):
  > *"Sahil Barua is the Managing Director and Chief Executive Officer of our Company."*
* **Source B**: *02-delhivery-industry-report.pdf* (Physical Page 30 / Section: Board of Directors):
  > *"Sahil Barua, Managing Director and Chief Executive Officer"*
* **System Reasoning**: Entity (`Sahil Barua`), Attribute (`designation`), and Normalized Value (`Managing Director and Chief Executive Officer`) match across independent filings with persistent temporal validity. **Status: CORROBORATED**.

---

### Case 2: A Genuine Contradiction
* **Fact**: Restated Loss for Fiscal Year 2021.
* **Source A**: *01-delhivery-drhp.pdf* (Physical Page 4):
  > *"Restated loss for the year: ₹(4,157.43) million"*
* **Source B**: *03-delhivery-update.pdf* (Physical Page 2):
  > *"Restated loss for the year: ₹(415.7) million"*
* **System Reasoning**: Both documents refer to the exact same fiscal entity, attribute (`restated_loss`), and temporal period (`FY2021`), yet state irreconcilable scalar magnitudes (`₹4,157.43M` vs `₹415.7M`). The engine flags this as a **high-severity numerical contradiction** caused by a clerical omission of the trailing digit. **Status: DIRECT CONTRADICTION**.

---

### Case 3: Apparent Contradiction Explained by Context (Time, Scope, Units)
* **Fact**: Revenue from Operations for Fiscal 2021.
* **Source A**: *01-delhivery-drhp.pdf* (Physical Page 5):
  > *"Revenue from operations: ₹36,465.28 million"*
* **Source B**: *01-delhivery-drhp.pdf* (Physical Page 22):
  > *"Revenue from operations: ₹44,505.00 million"*
* **Context Decomposition**:
  - **Temporal / Period Delta**: Source A represents the **Restated 9-Month Period ended December 31, 2020**, whereas Source B represents the **Full Audited Fiscal Year 2021 ended March 31, 2021**.
  - **Reconciliation**: The reconciliation engine checks the temporal bounds and prevents a false-positive conflict warning, generating a human-readable explanation of why both statements are mathematically sound within their respective frames. **Status: CONTEXTUALLY EXPLAINED**.

---

### Case 4: Extraction Failure & Architectural Remediation
* **Failure Scenario**: Boilerplate Pollution in Corporate Header Addresses.
* **Document**: *01-delhivery-drhp.pdf* (Physical Page 1).
* **Problematic Raw Extraction**: Naive regex captured legal header tags: `"Plot No. 5, Sector 44, Gurugram 122 002, Haryana, India (CORPORATE)"`.
* **Root Cause**: PDF cover pages contain bracketed legal annotations adjacent to registered office definitions that pollute raw substring extractions.
* **Architectural Remediation**:
  1. The confidence scoring engine flags records with bracketed institutional boilerplate (confidence `< 0.70`).
  2. The sanitizer normalizes legal suffixes, extracts the clean address entity (`Plot No. 5, Sector 44, Gurugram 122 002, Haryana, India`), and logs a human-in-the-loop audit trace. **Status: MITIGATED & RECOVERED**.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | FastAPI, Uvicorn, Pydantic v2 |
| **PDF Ingestion & Extraction** | PyMuPDF (`fitz`), pdfplumber, Regex Tokenizer |
| **3D Graph Visualization** | Three.js, 3D-Force-Graph (WebGL) |
| **Styling & Design System** | Synthetix Cyberpunk Brutalism (Vanilla CSS & JS) |
| **CLI Engine** | Rich, Typer |
| **Optional LLM Providers** | Google Gemini (`google-generativeai`), OpenAI API |

---

## ⚠️ Limitations and Next Steps

### Current Limitations
1. **Scanned / Raster-Only PDFs**: FactMesh is optimized for vector/text-native PDFs (which represent >95% of institutional filings, earnings reports, and SEBI/SEC prospectuses). Scanned image-only PDFs without an embedded OCR text layer require an upstream OCR engine.
2. **Deeply Nested Multi-Tier Tables**: While standard 2D vector tables are accurately segmented via `page.find_tables()`, tables with 3+ tiers of merged row/column super-headers can flatten into merged strings in edge cases.
3. **Cross-Language Extractions**: Currently tuned for English-language documents and standard financial/corporate notation (Indian Lakhs/Crores, Western Millions/Billions, standard currency symbols ₹, $, €, £).

### Next Steps & Future Roadmap
1. **Integrated OCR Layer**: Incorporate local Tesseract OCR fallback to automatically process historical scanned documents without external cloud dependencies.
2. **4D Temporal Scrubber in 3D Graph**: Add an interactive time-scrubber widget directly inside the Three.js canvas to watch corporate metrics and graph edges evolve dynamically across fiscal quarters and years.
3. **Local Small Language Models (SLMs)**: Support local quantized models (e.g., Phi-3-mini or Gemma 2 2B via `llama.cpp` or Ollama) for complex open-domain multi-paragraph narrative synthesis with 100% offline privacy.
4. **Exportable Audit Pack**: One-click export of reconciled fact matrices to interactive Excel / CSV tables with clickable deep-links directly opening the PDF to the cited page.

---

## 📝 Additional Notes

- **Zero Credentials & 100% Offline Evaluation**: FactMesh requires **no paid services, no API keys, and no internet connection** to be completely evaluated. All parsing, physical page binding, cross-document reconciliation, 3D WebGL rendering, and REST endpoints execute locally.
- **Strict Provenance Guarantee**: Every fact in the system is immutably linked to its physical document name, 1-indexed physical page number, and verbatim quotation snippet. Hallucinated or floating ungrounded facts are architecturally impossible.
- **Stress-Tested Across Multiple Enterprise Filings**: Tested and verified on **Delhivery Limited** (DRHP, Industry Report, Updates), **Infosys Limited** (Q4 FY24 Financial Fact Sheet), **Apple Inc.** (10-K), and **Tesla Inc.** (Shareholder Deck).
- **Evaluation Without Account**: All sample outputs, verified cases, and deterministic extractors are included in the repository. Reviewers can clone the repo and run `python main.py` or `python cli.py cases --dataset delhivery` immediately.

---

## 📄 License & Attribution

Developed for the **Superjoin VIT 2026 Engineering Intern Hiring Assignment**.  
Design inspiration: Synthetix Cyberpunk Brutalism from [RepoWhisper](https://github.com/X-ImLucky-X/RepoWhisper).  
Licensed under the [MIT License](LICENSE).

