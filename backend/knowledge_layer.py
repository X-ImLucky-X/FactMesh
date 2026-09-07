import os
import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

from backend.models import (
    Fact,
    DocumentMetadata,
    FactRelationship,
    RelationshipType,
    KnowledgeGraph,
    GraphNode,
    GraphEdge,
    QueryResponse
)
from backend.ingestion import DocumentParser
from backend.fact_extractor import FactExtractor
from backend.reconciliation import ReconciliationEngine
from backend import config

logger = logging.getLogger("FactKnowledgeLayer")

class FactKnowledgeLayer:
    """
    Central Knowledge Layer holding extracted facts, source provenance,
    cross-document relationships, and interactive graph structures.
    Supports incremental ingestion, search, and dynamic indexing.
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or config.DATA_STORAGE_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.documents: Dict[str, DocumentMetadata] = {}
        self.facts: Dict[str, Fact] = {}  # fact_id -> Fact
        self.relationships: List[FactRelationship] = []
        self.extractor = FactExtractor()

    def ingest_document(self, file_path: str, run_reconciliation: bool = True) -> Dict[str, Any]:
        """
        Ingests a new PDF document incrementally:
        1. Parses pages and text blocks
        2. Extracts grounded facts
        3. Updates index
        4. Reconciles new facts against all existing facts without rebuilding old state.
        """
        path = Path(file_path)
        doc_data = DocumentParser.parse_pdf(path)
        metadata = doc_data["metadata"]

        # Extract facts from new document
        new_facts = self.extractor.extract_facts_from_document(doc_data)
        metadata.facts_count = len(new_facts)

        self.documents[metadata.filename] = metadata
        for f in new_facts:
            self.facts[f.id] = f

        # Incremental reconciliation: reconcile new facts against existing facts
        new_relationships = []
        if run_reconciliation:
            all_facts_list = list(self.facts.values())
            # Reconcile across all current facts
            self.relationships = ReconciliationEngine.reconcile_facts(all_facts_list)

        self.save_state()

        return {
            "document": metadata,
            "facts_extracted": len(new_facts),
            "total_facts": len(self.facts),
            "total_relationships": len(self.relationships)
        }

    def ingest_multiple(self, file_paths: List[str]) -> Dict[str, Any]:
        """Ingests a batch of PDF documents."""
        results = []
        for fp in file_paths:
            res = self.ingest_document(fp, run_reconciliation=False)
            results.append(res)

        # Run reconciliation once for the batch
        all_facts_list = list(self.facts.values())
        self.relationships = ReconciliationEngine.reconcile_facts(all_facts_list)
        self.save_state()

        return {
            "documents_ingested": len(results),
            "total_facts": len(self.facts),
            "total_relationships": len(self.relationships)
        }

    def get_facts(self,
                  document_filter: Optional[str] = None,
                  entity_filter: Optional[str] = None,
                  attribute_filter: Optional[str] = None,
                  query: Optional[str] = None) -> List[Fact]:
        """Retrieves facts filtered by criteria."""
        res = list(self.facts.values())

        if document_filter:
            res = [f for f in res if document_filter.lower() in f.document_name.lower()]
        if entity_filter:
            res = [f for f in res if entity_filter.lower() in f.entity.lower()]
        if attribute_filter:
            res = [f for f in res if attribute_filter.lower() in f.attribute.lower()]
        if query:
            q = query.lower()
            res = [f for f in res if q in f.entity.lower() or q in f.attribute.lower() or q in str(f.value).lower() or q in f.evidence.verbatim_quote.lower()]

        return res

    def get_relationships(self, rel_type: Optional[RelationshipType] = None) -> List[FactRelationship]:
        """Retrieves cross-document relationships, optionally filtered by type."""
        if not rel_type:
            return self.relationships
        return [r for r in self.relationships if r.relationship_type == rel_type]

    def build_knowledge_graph(self) -> KnowledgeGraph:
        """
        Builds graph network for interactive visualizer.
        Nodes: Documents, Entities, Facts.
        Edges: Extracted From, Mentions, Cross-Document Relationships.
        """
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        node_ids: Set[str] = set()

        # 1. Document Nodes
        for doc_name, meta in self.documents.items():
            doc_id = f"doc_{doc_name}"
            if doc_id not in node_ids:
                node_ids.add(doc_id)
                nodes.append(GraphNode(
                    id=doc_id,
                    label=doc_name,
                    type="document",
                    properties={"page_count": meta.page_count, "facts_count": meta.facts_count}
                ))

        # 2. Entity Nodes & Fact Nodes
        for fact_id, fact in self.facts.items():
            # Entity Node
            entity_id = f"entity_{fact.entity.replace(' ', '_').lower()}"
            if entity_id not in node_ids:
                node_ids.add(entity_id)
                nodes.append(GraphNode(
                    id=entity_id,
                    label=fact.entity,
                    type="entity",
                    properties={"name": fact.entity}
                ))

            # Fact Node
            f_node_id = f"fact_{fact.id[:8]}"
            if f_node_id not in node_ids:
                node_ids.add(f_node_id)
                nodes.append(GraphNode(
                    id=f_node_id,
                    label=f"{fact.attribute}: {fact.raw_value or fact.value}",
                    type="fact",
                    properties={
                        "attribute": fact.attribute,
                        "value": str(fact.value),
                        "period": fact.temporal_context or "",
                        "scope": fact.scope_context or "",
                        "page": fact.page_number,
                        "doc": fact.document_name
                    }
                ))

            # Edge: Document -> Fact (Contains / Provenance)
            edges.append(GraphEdge(
                id=f"edge_doc_{fact.id[:8]}",
                source=f"doc_{fact.document_name}",
                target=f_node_id,
                label=f"p. {fact.page_number}",
                properties={"page": fact.page_number}
            ))

            # Edge: Fact -> Entity (Pertains to)
            edges.append(GraphEdge(
                id=f"edge_ent_{fact.id[:8]}",
                source=f_node_id,
                target=entity_id,
                label="subject",
                properties={}
            ))

        # 3. Relationship Edges between Fact Nodes
        for rel in self.relationships:
            src_node = f"fact_{rel.source_fact_id[:8]}"
            tgt_node = f"fact_{rel.target_fact_id[:8]}"
            if src_node in node_ids and tgt_node in node_ids:
                edges.append(GraphEdge(
                    id=f"edge_rel_{rel.id[:8]}",
                    source=src_node,
                    target=tgt_node,
                    label=rel.relationship_type.value,
                    relationship_type=rel.relationship_type,
                    properties={"reasoning": rel.reasoning, "takeaway": rel.key_takeaway}
                ))

        return KnowledgeGraph(nodes=nodes, edges=edges)

    def answer_query(self, query: str) -> QueryResponse:
        """
        Natural language query interface over the fact layer.
        Finds supporting facts and generates evidence-grounded summary.
        """
        q = query.lower()
        matched_facts = []

        for fact in self.facts.values():
            # Check for keyword matches in entity, attribute, value, quote
            match_score = 0
            words = [w for w in re.findall(r'\w+', q) if len(w) > 2]
            for w in words:
                if w in fact.entity.lower():
                    match_score += 3
                if w in fact.attribute.lower():
                    match_score += 3
                if w in str(fact.value).lower():
                    match_score += 2
                if w in fact.evidence.verbatim_quote.lower():
                    match_score += 1

            if match_score > 0:
                matched_facts.append((match_score, fact))

        matched_facts.sort(key=lambda x: x[0], reverse=True)
        top_facts = [f[1] for f in matched_facts[:8]]

        # Find matching relationships
        top_fact_ids = {f.id for f in top_facts}
        related_rels = [
            r for r in self.relationships
            if r.source_fact_id in top_fact_ids or r.target_fact_id in top_fact_ids
        ]

        if not top_facts:
            answer = f"No direct facts found matching query '{query}'. Try exploring facts by document or uploading related PDFs."
        else:
            fact_summaries = []
            for f in top_facts[:4]:
                fact_summaries.append(
                    f"• {f.entity} - {f.attribute}: {f.raw_value or f.value} ({f.temporal_context or 'N/A'}, {f.document_name} p.{f.page_number})"
                )
            answer = f"Found {len(top_facts)} grounded facts matching your query:\n" + "\n".join(fact_summaries)
            if related_rels:
                answer += f"\n\nCross-Document Insights ({len(related_rels)} relationships found):\n"
                for r in related_rels[:2]:
                    answer += f"• [{r.relationship_type.value}]: {r.key_takeaway}\n"

        return QueryResponse(
            query=query,
            answer=answer,
            supporting_facts=top_facts,
            related_relationships=related_rels
        )

    def save_state(self):
        """Persists knowledge layer state to disk."""
        try:
            state_file = self.storage_dir / "knowledge_state.json"
            data = {
                "documents": {k: v.model_dump() for k, v in self.documents.items()},
                "facts": {k: v.model_dump() for k, v in self.facts.items()},
                "relationships": [r.model_dump() for r in self.relationships]
            }
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to persist state: {e}")

    def load_state(self):
        """Loads persisted state from disk if available."""
        state_file = self.storage_dir / "knowledge_state.json"
        if not state_file.exists():
            return
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.documents = {k: DocumentMetadata(**v) for k, v in data.get("documents", {}).items()}
            self.facts = {k: Fact(**v) for k, v in data.get("facts", {}).items()}
            self.relationships = [FactRelationship(**r) for r in data.get("relationships", [])]
        except Exception as e:
            logger.warning(f"Failed to load state: {e}")

    def clear(self):
        """Resets the knowledge layer."""
        self.documents.clear()
        self.facts.clear()
        self.relationships.clear()
        state_file = self.storage_dir / "knowledge_state.json"
        if state_file.exists():
            state_file.unlink()
