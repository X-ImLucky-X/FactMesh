import pytest
from fastapi.testclient import TestClient
from backend.api import app

client = TestClient(app)

def test_api_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "facts_count" in data

def test_api_four_cases_delhivery():
    response = client.get("/api/four-cases?dataset=delhivery")
    assert response.status_code == 200
    data = response.json()
    assert "case_1_corroboration" in data
    assert "case_2_contradiction" in data
    assert "case_3_apparent_contradiction_explained" in data
    assert "case_4_failure_and_remediation" in data
    assert data["case_1_corroboration"]["status"] == "CORROBORATED"

def test_api_four_cases_macro():
    response = client.get("/api/four-cases?dataset=india-macroeconomy")
    assert response.status_code == 200
    data = response.json()
    assert "case_1_corroboration" in data
    assert "8.2%" in data["case_1_corroboration"]["value"]

def test_api_query():
    response = client.post("/api/query", json={"query": "Who is the MD and CEO of Delhivery?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
