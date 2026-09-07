import pytest
from backend.fact_extractor import FactExtractor
from backend.models import FactType

def test_extract_financial_metrics():
    extractor = FactExtractor(provider="local")
    sample_text = """
    In FY24, Delhivery Limited reported revenue from operations of Rs 8,142 Cr and Adjusted EBITDA of Rs 127 Cr.
    The express parcel revenue stood at Rs 5,077 Cr in FY24.
    """
    facts = extractor.extract_facts_from_page("test_report.pdf", 1, sample_text)
    assert len(facts) >= 2

    # Check revenue fact
    rev_fact = next((f for f in facts if "Revenue" in f.attribute), None)
    assert rev_fact is not None
    assert rev_fact.value == 8142.0
    assert rev_fact.temporal_context == "FY24"
    assert rev_fact.evidence.page_number == 1
    assert "8,142" in rev_fact.evidence.verbatim_quote

def test_extract_macro_metrics():
    extractor = FactExtractor(provider="local")
    sample_text = """
    India's Real GDP growth was 8.2% in FY24, while headline CPI inflation averaged 5.4% in 2024-25.
    """
    facts = extractor.extract_facts_from_page("test_macro.pdf", 5, sample_text)
    assert len(facts) >= 2

    gdp_fact = next((f for f in facts if "GDP" in f.attribute), None)
    assert gdp_fact is not None
    assert gdp_fact.value == 8.2
    assert gdp_fact.unit == "%"
    assert gdp_fact.temporal_context == "FY24"

def test_extract_governance_metrics():
    extractor = FactExtractor(provider="local")
    sample_text = """
    Sahil Barua serves as Managing Director & Chief Executive Officer of Delhivery Limited.
    """
    facts = extractor.extract_facts_from_page("test_gov.pdf", 2, sample_text)
    assert len(facts) >= 1
    gov_fact = facts[0]
    assert "Sahil Barua" in gov_fact.entity
    assert "Managing Director" in str(gov_fact.value)
