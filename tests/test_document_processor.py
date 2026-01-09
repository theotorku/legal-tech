import types
from services.document_processor import ContractProcessor


def test_process_returns_text_and_metadata(monkeypatch):
    # Create fake document object
    class FakeDoc:
        def __init__(self):
            self.pages = [1, 2]

        def export_to_markdown(self):
            return "# Contract\nThis is a contract."

    class FakeResult:
        def __init__(self):
            self.document = FakeDoc()

    class FakeConverter:
        def convert(self, path):
            return FakeResult()

    monkeypatch.setattr(
        "services.document_processor.DocumentConverter", lambda: FakeConverter())

    p = ContractProcessor()
    out = p.process("dummy.pdf")

    assert "text" in out and out["text"].startswith("# Contract")
    assert out["metadata"]["filename"] == "dummy.pdf"
    assert out["metadata"]["pages"] == 2
