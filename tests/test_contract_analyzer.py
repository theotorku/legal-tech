import json
from types import SimpleNamespace
from services.contract_analyzer import ContractAnalyzer


class DummyChoiceMsg:
    def __init__(self, content):
        self.message = SimpleNamespace(content=content)


class DummyResponse:
    def __init__(self, content):
        self.choices = [DummyChoiceMsg(content)]


def test_analyze_parses_json(monkeypatch):
    sample_json = json.dumps({
        "contract_type": "NDA",
        "parties": ["Company A", "Company B"],
        "key_dates": [],
        "key_terms": ["confidentiality"],
        "risk_level": "Low",
        "summary": "Short summary"
    })

    def fake_create(*args, **kwargs):
        return DummyResponse(sample_json)

    # Monkeypatch the module helper used by the analyzer via the module object
    import importlib
    mod = importlib.import_module("services.contract_analyzer")
    monkeypatch.setattr(mod, "_chat_create", fake_create)

    analyzer = ContractAnalyzer()
    res = analyzer.analyze("some text")

    assert res.contract_type == "NDA"
    assert "Company A" in res.parties
    assert res.risk_level == "Low"
