# Fact Knowledge Layer: Cross-Document Intelligence & Semantic Reconciliation

> **Superjoin VIT 2026 Engineering Intern Hiring Assignment**  
> An open-domain, schema-flexible Fact Knowledge Layer that extracts grounded facts from multi-document collections, links them to exact page evidence, discovers cross-document relationships (corroborations, contradictions, and contextual divergence), and provides interactive Web UI, REST API, and CLI inspection tools.

---

## 🌟 Key Highlights

- **Grounding to Source Evidence**: Every extracted fact retains its 1-indexed document page number, verbatim quotation snippet, and bounding paragraph context.
- **Hybrid Semantic & Reasoning Engine**: Runs out-of-the-box in 100% offline local mode without external API dependencies, and seamlessly leverages LLMs (Gemini / OpenAI) when API keys are provided.
- **Multi-Dimensional Fact Reconciliation**: Identifies corroborations (even across differing terminologies and unit scales), genuine contradictions (direct institutional or reporting conflicts), and apparent contradictions explained by temporal growth, accounting scope, or basket definitions.
- **Incremental Knowledge Indexing**: Ingests new PDF documents incrementally without rebuilding previously established knowledge layers.
- **Multi-Modal Access**: Full-featured Web Dashboard + Interactive Knowledge Graph + Swagger REST API (`/docs`) + Rich Terminal CLI.

---

## 🚀 Setup and Run Instructions

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.11)
- `pip` package manager

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/your-username/fact-knowledge-layer.git
cd fact-knowledge-layer
pip install -r requirements.txt
```

### 3. (Optional) Configure Cloud LLM API Keys
The system runs completely offline without any API keys. If you wish to enable cloud LLM-assisted extraction:
```bash
cp .env.example .env
# Edit .env and set GEMINI_API_KEY or OPENAI_API_KEY
```

### 4. Running the Web Application & REST API
Start the FastAPI server:
```bash
python main.py
```
Open your browser at:
- **Interactive UI Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Interactive REST API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Running via CLI
You can also run batch ingestion and inspection directly from the terminal:

```bash
# 1. Ingest Delhivery starter dataset
python cli.py load --dataset delhivery

# 2. View the Four Required Cases with full evidence & reasoning
python cli.py cases --dataset delhivery

# 3. Ingest India Macroeconomy dataset
python cli.py load --dataset india-macroeconomy
python cli.py cases --dataset india-macroeconomy

# 4. Explore extracted facts
python cli.py facts --limit 20

# 5. Ingest custom PDFs
python cli.py ingest path/to/document1.pdf path/to/document2.pdf

# 6. Ask natural language questions with source grounding
python cli.py query "What is the Real GDP growth rate of India in FY24?"
```

### 6. Running the Automated Test Suite
Run the full pytest suite:
```bash
python -m pytest tests/ -v
```

---

## 📹 Video Demo

- **Demo Video Link**: `[Link to 3-minute Loom / YouTube / Drive Demo Video]` *(Record a short walkthrough showing PDF ingestion, the four cases showcase, knowledge graph navigation, and Q&A)*
- **Demo Highlights Checklist**:
  1. Ingesting starter PDF documents (`delhivery/` and `india-macroeconomy/`).
  2. Demonstrating Case 1: Corroboration across multiple filings.
  3. Demonstrating Case 2: Genuine Contradiction.
  4. Demonstrating Case 3: Apparent Contradiction resolved by context (time/units/scope).
  5. Demonstrating Case 4: Table column alignment failure discovery and architectural remediation.
  6. Interactive knowledge graph exploration and custom PDF drag-and-drop upload.

---

## 🧠 Approach & Architecture

### System Architecture Diagram
```
                          ┌────────────────────────┐
                          │   PDF Document Stream  │
                          └───────────┬────────────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │  PyMuPDF Parser & Text │
                          │  Block Chunker Engine  │
                          └───────────┬────────────┘
                                      │
                                      ▼
                      ┌────────────────────────────────┐
                      │    Hybrid Fact Extractor       │
                      │  • Local Semantic Patterns     │
                      │  • LLM Structured JSON Schema  │
                      └───────────────┬────────────────┘
                                      │ (Facts + Exact Page Quotes)
                                      ▼
                      ┌────────────────────────────────┐
                      │ Incremental Knowledge Layer    │
                      │  • Entity-Attribute Index      │
                      │  • Multi-PDF Graph Topology    │
                      └───────────────┬────────────────┘
                                      │
                                      ▼
                      ┌────────────────────────────────┐
                      │ Cross-Document Reconciliation  │
                      │  • Corroboration Matcher       │
                      │  • Contradiction Detector      │
                      │  • Context Delta Decomposer    │
                      └───────────────┬────────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            ▼                         ▼                         ▼
   ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
   │ Interactive UI  │      │  FastAPI /docs  │      │ Rich Python CLI │
   │ Dashboard+Graph │      │  REST Endpoints │      │  Terminal Tool  │
   └─────────────────┘      └─────────────────┘      └─────────────────┘
```

### 1. Document Ingestion & Grounding (`backend/ingestion.py`)
- High-performance PDF parser using `PyMuPDF` (`fitz`) that preserves exact 1-indexed document page coordinates matching printed physical documents.
- Extracts structural bounding boxes and captures surrounding sentence windows to maintain complete contextual provenance.

### 2. Open-Domain Hybrid Fact Extraction (`backend/fact_extractor.py`)
- Extracts structured multi-field facts: `(entity, attribute, value, raw_value, unit, temporal_context, scope_context, verbatim_quote, page_number, confidence)`.
- Normalizes disparate currency metrics (e.g. converting `₹81,420 Mn` and `₹8,142 Cr` into standardized base units for apples-to-apples comparison).

### 3. Multi-Dimensional Reconciliation Engine (`backend/reconciliation.py`)
Compares cross-document fact clusters along four orthogonal context axes:
1. **Value Equivalence**: Numerical tolerance matching and semantic token overlap.
2. **Temporal Delta**: Isolating distinct fiscal periods (e.g. FY22 vs FY24).
3. **Scope / Segment Delta**: Differentiating consolidated totals from subsidiary or service segment metrics (e.g. Express Parcel vs Consolidated).
4. **Unit / Reporting Vintage**: Normalizing scale differences and detecting statistical revisions (Advance vs Provisional vs Actual).

### 4. Important Engineering Decisions & Trade-offs
- **Self-Contained Offline Reliability vs LLM Flexibility**: Instead of hard-depending on paid third-party APIs (which can fail due to rate limits or missing credentials), the core engine features an offline-first deterministic extractor and reconciler, while seamlessly integrating cloud LLMs when configured.
- **Incremental Ingestion vs Full Re-indexing**: Ingesting a new document indexes its facts and matches against existing facts in $O(N \cdot M)$ comparison time without re-parsing historical PDFs.
- **Glassmorphism Web UI**: Built with lightweight zero-dependency vanilla JS and CSS to ensure instant load times and zero build-step overhead.

---

## 🎯 Show Us These Four Cases

### Case 1: Fact Corroborated Across Documents (Even If Phrased Differently)
* **Entity**: Sahil Barua
* **Attribute**: Executive Leadership / Designation at Delhivery Limited
* **Corroborated Status**: `CORROBORATED`
* **Source Evidence**:
  1. *Delhivery Prospectus 2022 (p. 250)*: `"Sahil Barua is the Managing Director and Chief Executive Officer of our Company."`
  2. *Delhivery Annual Report FY24 (p. 8)*: `"Sahil Barua (DIN: 05131570) Managing Director & CEO"`
  3. *Delhivery Q4 FY24 Earnings Presentation (p. 2)*: `"Management Commentary by Sahil Barua, MD & CEO"`
* **System Reasoning**: The engine identifies the entity `'Sahil Barua'` across three documents spanning 2022 to 2024. Despite phrasing variations (`"Managing Director and Chief Executive Officer"`, `"MD & CEO"`, `"Managing Director & CEO"`), the semantic normalizer aligns executive titles and validates persistent corporate leadership across all filings.

*(Macroeconomy Example)*: Headline Real GDP growth rate for FY24 (**8.2%**) is unanimously corroborated across the *Economic Survey 2024-25* (p. 46), *RBI Annual Report 2024-25* (p. 27), and *IMF Article IV Consultation* (p. 4).

---

### Case 2: A Genuine or Likely Contradiction
* **Entity**: Indian Economy
* **Attribute**: Projected Real GDP Growth Rate for FY25 (2024-25)
* **Contradiction Status**: `CONTRADICTION`
* **Source Evidence**:
  1. *RBI Annual Report 2024-25 (p. 28)*: `"Real GDP growth for 2024-25 is projected at 7.2 per cent, with risks evenly balanced around this baseline."`
  2. *IMF Article IV Consultation 2025 (p. 4)*: `"Growth is projected to moderate to 7.0 percent in FY2024/25 as cyclical tailwinds normalize."`
  3. *Economic Survey 2024-25 (p. 48)*: `"The Survey conservatively projects real GDP growth of 6.5 to 7.0 per cent in FY25."`
* **System Reasoning**: The system detected non-overlapping point estimates for the exact same forward-looking period (`FY25`) and metric. This is a genuine institutional forecast contradiction arising from differing analytical models regarding global trade headwinds and domestic consumption trajectories.

*(Delhivery Example)*: Pre-IPO Prospectus CCPS fair-value loss disclosures vs Post-IPO Annual Report restatements of prior period operating losses under Ind-AS reclassifications.

---

### Case 3: Apparent Contradiction Explained by Context (Time, Scope, Units)
* **Entity**: Delhivery Limited
* **Attribute**: Revenue from Operations
* **Resolution Status**: `APPARENT_CONTRADICTION_EXPLAINED`
* **Source Evidence**:
  1. *Delhivery Prospectus 2022 (p. 30)*: `"Total Revenue from Operations for the fiscal year ended March 31, 2022 was ₹68,813.00 Million (₹6,881.30 Cr)."` *(FY22, Consolidated)*
  2. *Delhivery Annual Report FY24 (p. 10)*: `"Revenue from Operations grew 13% YoY to reach ₹8,142 Crore in FY24 from ₹7,225 Crore in FY23."` *(FY24, Consolidated)*
  3. *Delhivery Q4 FY24 Presentation (p. 16)*: `"Full Year FY24 Revenue from Operations stood at ₹81,420 Mn with Express Parcel contributing ₹50,770 Mn."` *(FY24, Consolidated vs Segment)*
* **Contextual Breakdown**:
  - **Temporal Delta**: ₹6,881 Cr (FY22) vs ₹8,142 Cr (FY24) reflects 18.3% multi-year business expansion rather than a data discrepancy.
  - **Unit Delta**: ₹8,142 Crore vs ₹81,420 Million is reconciled via unit conversion ($81,420 \text{ Mn} / 10 = 8,142 \text{ Cr}$).
  - **Scope Delta**: Express Parcel revenue (₹5,077 Cr) vs Total Revenue (₹8,142 Cr) is reconciled via segment decomposition (Express Parcel represents ~62.4% of total revenues).
* **System Reasoning**: Multi-dimensional context decomposition automatically normalizes unit scales, isolates fiscal years, and tags segment boundaries, resolving what would otherwise appear as incompatible revenue disclosures.

---

### Case 4: Extraction or Reasoning Failure Found & How It Was Handled / Mitigated
* **Failure Title**: Multi-Period Financial Table Column Shift & Footnote Detachment
* **Document**: `01-delhivery-prospectus-2022-excerpt.pdf` (Page 30, Summary Financial Statements)
* **Problematic Raw Extraction**: Naive linear text extraction merged adjacent table columns into a single line, causing extractors to mistakenly bind FY20 revenue (₹29,886 Mn) to the FY22 header.
* **Root Cause**: PDF text streams render text elements based on draw instructions rather than relational table matrices. Multi-column financial tables lose their horizontal cell boundaries when serialized linearly.
* **Handling & Remediation**:
  1. Implemented **2D Bounding Box Block Sorting** (`page.get_text('blocks')`) in PyMuPDF to reconstruct column coordinate envelopes.
  2. Integrated **Header Scale Marker Detection** that captures unit multipliers (e.g. `(₹ in Millions)`) from table banners and propagates them to all child column cells.
* **Fixed / Mitigated Output**: Correctly binds each metric to its corresponding column: FY22 = ₹6,881.30 Cr, FY21 = ₹4,450.53 Cr, FY20 = ₹2,988.63 Cr.

---

## 🛠️ Limitations and Next Steps

### Current Limitations
1. **Complex Scanned Visual Tables**: Documents containing rasterized bitmap tables without OCR text layers require an OCR preprocessing pipeline (e.g., Tesseract or Docling).
2. **Implicit Coreferences**: When a document refers to "the acquired entity" without naming Spoton Logistics in the immediate paragraph, multi-hop resolution is required.

### Next Steps & Production Roadmap
1. **Vector & Hybrid Retrieval Index**: Integrate FAISS / pgvector with hybrid BM25 dense-sparse search for sub-millisecond querying across millions of documents.
2. **Multi-Hop Graph Reasoning Agents**: Deploy LangGraph or multi-agent debate pipelines to iteratively verify ambiguous contradictions with deep verification loops.
3. **Automated PDF Bounding-Box Overlay in UI**: Render PDF pages with interactive visual highlights directly on the canvas corresponding to extracted quote coordinates.

---

## 📝 Additional Notes & Brownie Points

- **Large PDF Handling**: Features streaming generator-based chunking that processes 100+ page PDF excerpts without memory spikes.
- **Dynamic Schema Evolution**: Emergent attributes and entities are dynamically organized and displayed without requiring predefined database schemas.
- **Incremental Knowledge Update**: Supports drag-and-drop document uploading that connects new facts to existing knowledge layers in real-time.
- **Clean Architecture**: Strictly separated modules for ingestion, models, extraction, reconciliation, knowledge graph, API, and UI.
