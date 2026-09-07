import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.models import (
    Fact,
    FactRelationship,
    RelationshipType,
    KnowledgeGraph,
    DocumentMetadata,
    FourCasesShowcase,
    QueryRequest,
    QueryResponse
)
from backend.knowledge_layer import FactKnowledgeLayer
from backend.showcase_cases import get_showcase_cases, DELHIVERY_FOUR_CASES, INDIA_MACRO_FOUR_CASES
from backend import config

# Initialize Knowledge Layer
knowledge_layer = FactKnowledgeLayer()
knowledge_layer.load_state()

app = FastAPI(
    title="Fact Knowledge Layer API",
    description="Cross-Document Fact Extraction, Provenance Grounding, and Semantic Reconciliation Layer",
    version="1.0.0"
)

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = config.BASE_DIR / "frontend"

@app.get("/api/status")
def get_status():
    """System health check and overview statistics."""
    return {
        "status": "healthy",
        "documents_count": len(knowledge_layer.documents),
        "facts_count": len(knowledge_layer.facts),
        "relationships_count": len(knowledge_layer.relationships),
        "provider": config.DEFAULT_PROVIDER
    }

@app.post("/api/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Uploads one or multiple PDFs and ingests them into the Fact Knowledge Layer."""
    saved_paths = []
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF.")

        dest_path = config.UPLOAD_DIR / file.filename
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_paths.append(str(dest_path))

    result = knowledge_layer.ingest_multiple(saved_paths)
    return {
        "message": f"Successfully ingested {len(saved_paths)} PDF(s).",
        "details": result
    }

@app.post("/api/load-dataset")
def load_starter_dataset(dataset_name: str = Query("delhivery", description="Dataset name: 'delhivery' or 'india-macroeconomy'")):
    """Loads and processes all PDFs from the specified starter dataset folder."""
    target_dir = config.DATASET_DIR / dataset_name
    if not target_dir.exists():
        # Try finding partial match
        if "delhi" in dataset_name.lower():
            target_dir = config.DATASET_DIR / "delhivery"
        elif "macro" in dataset_name.lower() or "india" in dataset_name.lower():
            target_dir = config.DATASET_DIR / "india-macroeconomy"
        else:
            raise HTTPException(status_code=404, detail=f"Dataset directory '{dataset_name}' not found.")

    pdf_files = list(target_dir.glob("*.pdf"))
    if not pdf_files:
        raise HTTPException(status_code=404, detail=f"No PDF files found in {target_dir}")

    result = knowledge_layer.ingest_multiple([str(p) for p in pdf_files])
    return {
        "message": f"Successfully loaded dataset '{dataset_name}' ({len(pdf_files)} PDFs).",
        "details": result,
        "dataset": dataset_name
    }

@app.get("/api/documents", response_model=List[DocumentMetadata])
def get_documents():
    """Returns list of all ingested documents with metadata."""
    return list(knowledge_layer.documents.values())

@app.get("/api/facts", response_model=List[Fact])
def get_facts(
    doc: Optional[str] = Query(None, description="Filter by document name"),
    entity: Optional[str] = Query(None, description="Filter by entity name"),
    attribute: Optional[str] = Query(None, description="Filter by attribute name"),
    q: Optional[str] = Query(None, description="Free text search query")
):
    """Returns list of extracted facts with optional search & filtering."""
    return knowledge_layer.get_facts(
        document_filter=doc,
        entity_filter=entity,
        attribute_filter=attribute,
        query=q
    )

@app.get("/api/relationships", response_model=List[FactRelationship])
def get_relationships(
    type: Optional[RelationshipType] = Query(None, description="Filter by relationship type (CORROBORATED, CONTRADICTION, APPARENT_CONTRADICTION_EXPLAINED)")
):
    """Returns cross-document relationships discovered between facts."""
    return knowledge_layer.get_relationships(rel_type=type)

@app.post("/api/reconcile")
def run_reconciliation():
    """Re-runs cross-document reconciliation engine on all current facts."""
    from backend.reconciliation import ReconciliationEngine
    all_facts = list(knowledge_layer.facts.values())
    rels = ReconciliationEngine.reconcile_facts(all_facts)
    knowledge_layer.relationships = rels
    knowledge_layer.save_state()
    return {
        "message": f"Reconciliation complete. Found {len(rels)} cross-document relationships.",
        "relationships_count": len(rels)
    }

@app.get("/api/four-cases", response_model=FourCasesShowcase)
def get_four_cases(dataset: str = Query("delhivery", description="Dataset key: 'delhivery' or 'india-macroeconomy'")):
    """Returns the four required cases showcase with full evidence and system reasoning."""
    return get_showcase_cases(dataset)

@app.get("/api/graph", response_model=KnowledgeGraph)
def get_knowledge_graph():
    """Returns nodes and edges for the interactive Knowledge Graph."""
    return knowledge_layer.build_knowledge_graph()

@app.post("/api/query", response_model=QueryResponse)
def query_knowledge_layer(req: QueryRequest):
    """Answers natural language questions with source-grounded evidence citations."""
    return knowledge_layer.answer_query(req.query)

@app.post("/api/reset")
def reset_knowledge_layer():
    """Clears all facts, documents, and relationships."""
    knowledge_layer.clear()
    return {"message": "Knowledge layer reset successfully."}

# Serve frontend static assets
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def serve_frontend_index():
        return FileResponse(FRONTEND_DIR / "index.html")
