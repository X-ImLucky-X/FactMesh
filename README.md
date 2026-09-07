# 🌌 FactMesh: AI Fact Knowledge Layer & Cross-Document Intelligence

### Automated Evidence Grounding, Reconciliation & 3D Knowledge Command Center
**Hiring Assignment Submission: Superjoin VIT 2026 Engineering Intern**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Three.js](https://img.shields.io/badge/Three.js-3D%20WebGL-black.svg?logo=three.js&logoColor=white)](https://threejs.org/)
[![Repository](https://img.shields.io/badge/GitHub-FactMesh-BD00FF.svg?logo=github&logoColor=white)](https://github.com/X-ImLucky-X/FactMesh)

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

## 🏗️ System Architecture

```text
       ┌────────────────────────┐
       │   PDF Document Stream  │ (Prospectuses, Reports, Updates)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │  PyMuPDF Parser & Text │
       │  Block Coordinate Grid │
       └───────────┬────────────┘
                   │
                   ▼
   ┌────────────────────────────────┐
   │     Hybrid Fact Extractor      │
   │  • Deterministic Regex & AST   │
   │  • Normalized Units & Scales   │
   │  • Exact Page Quote Bounder    │
   └───────────────┬────────────────┘
                   │
                   ▼
   ┌────────────────────────────────┐
   │  Incremental Knowledge Layer   │
   │  • Entity-Attribute Index      │
   │  • Multi-PDF Graph Topology    │
   └───────────────┬────────────────┘
                   │
                   ▼
   ┌────────────────────────────────┐
   │ Cross-Document Reconciliation  │
   │  • Corroboration Engine        │
   │  • Contradiction Detector      │
   │  • Multi-Axis Delta Decomposer │
   └───────────────┬────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
┌──────────────────┐  ┌──────────────────┐
│  Next-Gen Web UI │  │ FastAPI REST API │
│  3D Force Graph  │  │   /docs Swagger  │
└──────────────────┘  └──────────────────┘
```

---

## 🚀 Getting Started

### 1. Clone Repository
```bash
git clone https://github.com/X-ImLucky-X/FactMesh.git
cd FactMesh
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Cloud LLM Keys
The application operates 100% locally by default. If you want hybrid LLM parsing:
```bash
cp .env.example .env
# Set GEMINI_API_KEY or OPENAI_API_KEY in .env
```

### 4. Run the Web Command Center
```bash
python main.py
```
Open your browser at:
- **Command Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Interactive REST API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. CLI Execution
You can also run batch extraction and queries via terminal:
```bash
# Ingest Delhivery dataset
python cli.py load --dataset delhivery

# Display the Four Core Cases
python cli.py cases --dataset delhivery

# Ingest custom PDFs
python cli.py ingest path/to/document1.pdf path/to/document2.pdf

# Ask questions with verified citations
python cli.py query "What was Delhivery's revenue growth across filings?"
```

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

## 📹 Video Walkthrough Plan (≤ 3:00 Minutes)

1. **0:00 – 0:30**: Introduction, problem statement (why flat RAG fails), and Synthetix Command Center overview.
2. **0:30 – 1:15**: Ingesting the Delhivery dataset live, verifying 197 facts and physical page citations.
3. **1:15 – 2:00**: Walking through the Four Core Cases (Corroboration, Contradiction, Apparent Contradiction, and Failure Mitigation).
4. **2:00 – 2:30**: Exploring the **3D Force Graph**: orbit rotation, photon particle pulses, and the sliding node inspector drawer.
5. **2:30 – 3:00**: Testing novel unseen PDFs via dynamic discovery mode, showing zero hardcoded dependencies.

---

## 📄 License & Attribution

Developed for the **Superjoin VIT 2026 Engineering Intern Hiring Assignment**.  
Design inspiration: Synthetix Cyberpunk Brutalism from [RepoWhisper](https://github.com/X-ImLucky-X/RepoWhisper).  
Licensed under the [MIT License](LICENSE).
