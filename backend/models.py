from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
import uuid
import datetime

class FactType(str, Enum):
    NUMERICAL = "NUMERICAL"
    CATEGORICAL = "CATEGORICAL"
    EXISTENTIAL = "EXISTENTIAL"
    RELATIONAL = "RELATIONAL"
    STATUS = "STATUS"

class RelationshipType(str, Enum):
    CORROBORATED = "CORROBORATED"
    CONTRADICTION = "CONTRADICTION"
    APPARENT_CONTRADICTION_EXPLAINED = "APPARENT_CONTRADICTION_EXPLAINED"
    EVOLUTION_OVER_TIME = "EVOLUTION_OVER_TIME"
    UNRELATED = "UNRELATED"

class Evidence(BaseModel):
    document_name: str
    page_number: int  # 1-indexed page number matching PDF
    verbatim_quote: str
    context_window: str = ""
    char_offset: Optional[int] = None
    section_title: Optional[str] = None

class Fact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_name: str
    page_number: int
    entity: str  # e.g., "Delhivery Limited", "Sahil Barua", "Indian Economy"
    attribute: str  # e.g., "Revenue from Operations", "Designation", "Active PIN Codes Served", "Real GDP Growth Rate"
    value: Union[float, int, str, bool]
    raw_value: str = ""  # exact representation in text
    unit: Optional[str] = None  # e.g., "₹ Cr", "%", "PIN codes", "Million"
    temporal_context: Optional[str] = None  # e.g., "FY24", "Q4 FY24", "March 31, 2022", "2024-25"
    scope_context: Optional[str] = None  # e.g., "Consolidated", "Standalone", "Express Parcel", "General Government"
    fact_type: FactType = FactType.NUMERICAL
    confidence: float = 0.95
    evidence: Evidence
    normalized_value: Optional[float] = None  # Standardized numerical value (e.g. in INR Crores or percentage)
    created_at: str = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

class ContextDelta(BaseModel):
    has_time_mismatch: bool = False
    time_delta: Optional[str] = None
    has_scope_mismatch: bool = False
    scope_delta: Optional[str] = None
    has_unit_mismatch: bool = False
    unit_delta: Optional[str] = None
    has_methodology_mismatch: bool = False
    methodology_delta: Optional[str] = None
    summary_explanation: str = ""

class FactRelationship(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_fact_id: str
    target_fact_id: str
    source_fact: Optional[Fact] = None
    target_fact: Optional[Fact] = None
    relationship_type: RelationshipType
    confidence: float = 0.9
    reasoning: str  # Comprehensive step-by-step reasoning
    context_delta: Optional[ContextDelta] = None
    key_takeaway: str = ""

class FailureCaseAnalysis(BaseModel):
    failure_title: str
    failure_type: str  # e.g., "Table Column Shift / Multi-period Header Mismatch", "Homonym / Scope Coreference"
    document_name: str
    page_number: int
    raw_text_snippet: str
    problematic_extraction: str
    root_cause: str
    handling_and_remediation: str  # What we handled or how to improve it
    fixed_or_mitigated_output: str

class FourCasesShowcase(BaseModel):
    dataset_name: str
    case_1_corroboration: Dict[str, Any]
    case_2_contradiction: Dict[str, Any]
    case_3_apparent_contradiction_explained: Dict[str, Any]
    case_4_failure_and_remediation: FailureCaseAnalysis

class DocumentMetadata(BaseModel):
    filename: str
    filepath: str
    page_count: int
    file_size_bytes: int
    facts_count: int = 0
    ingested_at: str = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # "document", "entity", "fact", "attribute"
    properties: Dict[str, Any] = Field(default_factory=dict)

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str
    relationship_type: Optional[RelationshipType] = None
    properties: Dict[str, Any] = Field(default_factory=dict)

class KnowledgeGraph(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)

class QueryRequest(BaseModel):
    query: str
    document_filter: Optional[List[str]] = None
    entity_filter: Optional[str] = None

class QueryResponse(BaseModel):
    query: str
    answer: str
    supporting_facts: List[Fact] = Field(default_factory=list)
    related_relationships: List[FactRelationship] = Field(default_factory=list)
