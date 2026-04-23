"""Testes do fluxo inicial de pulseira vinculada à pessoa monitorada."""
import pyotp

from fastapi.testclient import TestClient


def _fazer_login_completo(client: TestClient, totp_secret: str) -> str:
    codigo = pyotp.TOTP(totp_secret).now()
    resposta = client.post("/auth/login", json={
        "email": "pietro@fallsense.com",
        "senha": "Senha123!",
        "codigo_2fa": codigo,
    })
    return resposta.json()["access_token"]


def _cadastrar_monitorado(client: TestClient, token: str, nome: str) -> int:
    resposta = client.post(
        "/monitorados",
        json={"nome_completo": nome},
        headers={"Authorization": f"Bearer {token}"},
    )
    return resposta.json()["id"]


def test_cadastrar_pulseira_vinculada_a_monitorado(client: TestClient, usuario_registrado):
    token = _fazer_login_completo(client, usuario_registrado["totp_secret"])
    pessoa_id = _cadastrar_monitorado(client, token, "Vó Maria")

    resposta = client.post(
        "/pulseiras",
        json={
            "mac_address": "AA:BB:CC:DD:EE:01",
            "pessoa_monitorada_id": pessoa_id,
            "versao_firmware": "1.0.0",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["mac_address"] == "AA:BB:CC:DD:EE:01"
    assert dados["pessoa_monitorada_nome"] == "Vó Maria"
    assert dados["status_ativo"] is True


def test_listar_pulseiras_do_usuario(client: TestClient, usuario_registrado):
    token = _fazer_login_completo(client, usuario_registrado["totp_secret"])
    pessoa_id = _cadastrar_monitorado(client, token, "Vó Maria")

    client.post(
        "/pulseiras",
        json={
            "mac_address": "AA:BB:CC:DD:EE:01",
            "pessoa_monitorada_id": pessoa_id,
            "versao_firmware": "1.0.0",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    resposta = client.get(
        "/pulseiras",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 200
    dados = resposta.json()
    assert len(dados) == 1
    assert dados[0]["mac_address"] == "AA:BB:CC:DD:EE:01"
    assert dados[0]["pessoa_monitorada_nome"] == "Vó Maria"
