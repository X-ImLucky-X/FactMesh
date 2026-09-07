import pytest
from pathlib import Path
from backend.ingestion import DocumentParser
from backend import config

def test_parse_pdf_delhivery():
    pdf_path = config.DATASET_DIR / "delhivery" / "03-delhivery-q4-fy24-earnings-presentation.pdf"
    if not pdf_path.exists():
        pytest.skip(f"Test PDF not found at {pdf_path}")

    res = DocumentParser.parse_pdf(pdf_path)
    assert res is not None
    assert "metadata" in res
    assert "pages" in res
    assert res["metadata"].page_count > 0
    assert len(res["pages"]) == res["metadata"].page_count
    assert res["total_chars"] > 1000

def test_extract_context_window():
    text = "The company recorded revenue from operations of Rs 8142 Cr in FY24, representing solid growth."
    quote = "revenue from operations of Rs 8142 Cr"
    ctx = DocumentParser.extract_context_window(text, quote, window_chars=20)
    assert quote in ctx
    assert len(ctx) >= len(quote)
