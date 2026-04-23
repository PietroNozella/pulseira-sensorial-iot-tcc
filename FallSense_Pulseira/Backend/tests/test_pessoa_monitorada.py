"""Testes do primeiro fluxo de domínio para pessoa monitorada."""
from fastapi.testclient import TestClient


def _fazer_login_completo(client: TestClient, totp_secret: str) -> str:
    import pyotp

    codigo = pyotp.TOTP(totp_secret).now()
    resposta = client.post("/auth/login", json={
        "email": "pietro@fallsense.com",
        "senha": "Senha123!",
        "codigo_2fa": codigo,
    })
    return resposta.json()["access_token"]


def test_cadastrar_pessoa_monitorada(client: TestClient, usuario_registrado):
    """Usuário autenticado deve conseguir cadastrar uma pessoa monitorada."""
    token = _fazer_login_completo(client, usuario_registrado["totp_secret"])

    resposta = client.post(
        "/monitorados",
        json={"nome_completo": "Vó Maria"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["nome_completo"] == "Vó Maria"
    assert "id" in dados


def test_listar_pessoas_monitoradas_do_usuario(client: TestClient, usuario_registrado):
    """Listagem deve retornar apenas as pessoas vinculadas ao usuário autenticado."""
    token = _fazer_login_completo(client, usuario_registrado["totp_secret"])

    client.post(
        "/monitorados",
        json={"nome_completo": "Vó Maria"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/monitorados",
        json={"nome_completo": "Seu José"},
        headers={"Authorization": f"Bearer {token}"},
    )

    resposta = client.get(
        "/monitorados",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 200
    dados = resposta.json()
    assert len(dados) == 2
    assert dados[0]["nome_completo"] == "Vó Maria"
    assert dados[1]["nome_completo"] == "Seu José"
