from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    resposta = client.get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}
