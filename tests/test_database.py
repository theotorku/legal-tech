from types import SimpleNamespace
import services.database as db_mod


class FakeTable:
    def insert(self, payload):
        class ExecRes:
            def __init__(self):
                self.data = [payload]
                self.error = None

            def execute(self):
                return SimpleNamespace(data=self.data, error=self.error)

        return ExecRes()


class FakeClient:
    def __init__(self):
        pass

    def table(self, name):
        return FakeTable()


def test_insert_contract(monkeypatch):
    monkeypatch.setattr(db_mod, "create_client", lambda url, key: FakeClient())

    svc = db_mod.SupabaseService(url="https://x", key="secret")
    metadata = {"filename": "a.pdf", "pages": 1}
    analysis = {"contract_type": "NDA", "summary": "ok"}

    res = svc.insert_contract(metadata, analysis)
    assert res["filename"] == "a.pdf"
    assert res["contract_type"] == "NDA"
