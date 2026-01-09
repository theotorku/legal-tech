import io
from fastapi.testclient import TestClient
import main
from services.contract_analyzer import ContractAnalysis


client = TestClient(main.app)


def test_analyze_endpoint(monkeypatch):
    # Stub processor.process
    monkeypatch.setattr(main.processor, "process", lambda path: {
                        "text": "contract text", "metadata": {"filename": "sample_contract.pdf", "pages": 1}})

    # Stub analyzer to return a ContractAnalysis instance
    ca = ContractAnalysis(contract_type="NDA", parties=["A", "B"], key_dates=[
    ], key_terms=[], risk_level="Low", summary="ok")
    monkeypatch.setattr(main.analyzer, "analyze", lambda text: ca)

    # Remove db or stub insert
    monkeypatch.setattr(main, "db", None)

    files = {"file": ("sample_contract.pdf",
                      b"%PDF-1.4 fake", "application/pdf")}
    resp = client.post("/analyze", files=files)

    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "sample_contract.pdf"
    assert data["analysis"]["contract_type"] == "NDA"
