import pytest
from backend.models import Fact, Evidence, FactType, RelationshipType
from backend.reconciliation import ReconciliationEngine

def test_reconcile_corroboration():
    f1 = Fact(
        document_name="doc_a.pdf",
        page_number=10,
        entity="Delhivery Limited",
        attribute="Revenue from Operations",
        value=8142.0,
        raw_value="₹8,142 Cr",
        unit="₹ Cr",
        temporal_context="FY24",
        scope_context="Consolidated",
        fact_type=FactType.NUMERICAL,
        normalized_value=8142.0,
        evidence=Evidence(document_name="doc_a.pdf", page_number=10, verbatim_quote="Revenue ₹8,142 Cr in FY24")
    )
    f2 = Fact(
        document_name="doc_b.pdf",
        page_number=16,
        entity="Delhivery Limited",
        attribute="Revenue from Operations",
        value=81420.0,
        raw_value="₹81,420 Mn",
        unit="₹ Cr",
        temporal_context="FY24",
        scope_context="Consolidated",
        fact_type=FactType.NUMERICAL,
        normalized_value=8142.0,  # 81420 Mn / 10 = 8142 Cr
        evidence=Evidence(document_name="doc_b.pdf", page_number=16, verbatim_quote="Revenue from operations ₹81,420 Mn in FY24")
    )

    rel = ReconciliationEngine.compare_fact_pair(f1, f2)
    assert rel is not None
    assert rel.relationship_type == RelationshipType.CORROBORATED
    assert "corroboration" in rel.reasoning.lower()

def test_reconcile_apparent_contradiction_explained():
    f1 = Fact(
        document_name="prospectus_2022.pdf",
        page_number=30,
        entity="Delhivery Limited",
        attribute="Revenue from Operations",
        value=6881.3,
        raw_value="₹6,881.30 Cr",
        unit="₹ Cr",
        temporal_context="FY22",
        scope_context="Consolidated",
        fact_type=FactType.NUMERICAL,
        normalized_value=6881.3,
        evidence=Evidence(document_name="prospectus_2022.pdf", page_number=30, verbatim_quote="FY22 revenue stood at ₹6,881.3 Cr")
    )
    f2 = Fact(
        document_name="annual_report_fy24.pdf",
        page_number=10,
        entity="Delhivery Limited",
        attribute="Revenue from Operations",
        value=8142.0,
        raw_value="₹8,142 Cr",
        unit="₹ Cr",
        temporal_context="FY24",
        scope_context="Consolidated",
        fact_type=FactType.NUMERICAL,
        normalized_value=8142.0,
        evidence=Evidence(document_name="annual_report_fy24.pdf", page_number=10, verbatim_quote="Revenue grew to ₹8,142 Cr in FY24")
    )

    rel = ReconciliationEngine.compare_fact_pair(f1, f2)
    assert rel is not None
    assert rel.relationship_type == RelationshipType.APPARENT_CONTRADICTION_EXPLAINED
    assert rel.context_delta.has_time_mismatch is True

def test_reconcile_genuine_contradiction():
    f1 = Fact(
        document_name="rbi_report.pdf",
        page_number=28,
        entity="Indian Economy",
        attribute="Real GDP Growth Rate",
        value=7.2,
        raw_value="7.2%",
        unit="%",
        temporal_context="FY25",
        scope_context="National Accounts",
        fact_type=FactType.NUMERICAL,
        normalized_value=7.2,
        evidence=Evidence(document_name="rbi_report.pdf", page_number=28, verbatim_quote="Real GDP growth projected at 7.2 per cent in 2024-25")
    )
    f2 = Fact(
        document_name="imf_report.pdf",
        page_number=4,
        entity="Indian Economy",
        attribute="Real GDP Growth Rate",
        value=7.0,
        raw_value="7.0%",
        unit="%",
        temporal_context="FY25",
        scope_context="National Accounts",
        fact_type=FactType.NUMERICAL,
        normalized_value=7.0,
        evidence=Evidence(document_name="imf_report.pdf", page_number=4, verbatim_quote="Growth is projected to moderate to 7.0 percent in FY2024/25")
    )

    rel = ReconciliationEngine.compare_fact_pair(f1, f2)
    assert rel is not None
    assert rel.relationship_type == RelationshipType.CONTRADICTION
