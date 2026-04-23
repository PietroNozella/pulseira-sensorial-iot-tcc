"""Testes do fluxo inicial de telemetria das pulseiras."""
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


def _cadastrar_pulseira(client: TestClient, token: str, pessoa_id: int, mac: str) -> None:
    client.post(
        "/pulseiras",
        json={
            "mac_address": mac,
            "pessoa_monitorada_id": pessoa_id,
            "versao_firmware": "1.0.0",
        },
        headers={"Authorization": f"Bearer {token}"},
    )


def test_cadastrar_evento_telemetria(client: TestClient, usuario_registrado):
    token = _fazer_login_completo(client, usuario_registrado["totp_secret"])
    pessoa_id = _cadastrar_monitorado(client, token, "Vó Maria")
    _cadastrar_pulseira(client, token, pessoa_id, "AA:BB:CC:DD:EE:01")

    resposta = client.post(
        "/eventos",
        json={
            "mac_address": "AA:BB:CC:DD:EE:01",
            "tipo_evento": "QUEDA_DETECTADA",
            "coordenadas_gps": "-23.5505,-46.6333",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["tipo_evento"] == "QUEDA_DETECTADA"
    assert dados["pessoa_monitorada_nome"] == "Vó Maria"


def test_listar_eventos_telemetria(client: TestClient, usuario_registrado):
    token = _fazer_login_completo(client, usuario_registrado["totp_secret"])
    pessoa_id = _cadastrar_monitorado(client, token, "Vó Maria")
    _cadastrar_pulseira(client, token, pessoa_id, "AA:BB:CC:DD:EE:01")

    client.post(
        "/eventos",
        json={
            "mac_address": "AA:BB:CC:DD:EE:01",
            "tipo_evento": "QUEDA_DETECTADA",
            "coordenadas_gps": "-23.5505,-46.6333",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/eventos",
        json={
            "mac_address": "AA:BB:CC:DD:EE:01",
            "tipo_evento": "BATERIA_BAIXA",
            "coordenadas_gps": None,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    resposta = client.get(
        "/eventos",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 200
    dados = resposta.json()
    assert len(dados) == 2
    assert dados[0]["tipo_evento"] == "BATERIA_BAIXA"
    assert dados[1]["tipo_evento"] == "QUEDA_DETECTADA"
