"""
Testes de autenticação — cobre requisitos 1.1 a 1.12 do checklist de segurança.
"""
import pyotp
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# 1. Registro
# ---------------------------------------------------------------------------

def test_registro_sucesso(client: TestClient):
    """Usuário válido deve ser registrado com status 201."""
    resposta = client.post("/auth/registrar", json={
        "nome_completo": "Pietro Nozella",
        "email": "pietro@fallsense.com",
        "telefone": "11999999999",
        "senha": "Senha123"
    })
    assert resposta.status_code == 201
    dados = resposta.json()
    # Retorna totp_secret e recovery_codes apenas no registro
    assert "totp_secret" in dados
    assert "recovery_codes" in dados
    assert len(dados["recovery_codes"]) == 8


def test_registro_email_duplicado(client: TestClient, usuario_registrado):
    """Segundo cadastro com o mesmo e-mail deve retornar 400."""
    resposta = client.post("/auth/registrar", json={
        "nome_completo": "Pietro Nozella",
        "email": "pietro@fallsense.com",
        "telefone": "11999999999",
        "senha": "Senha123"
    })
    assert resposta.status_code == 400


def test_registro_senha_fraca_curta(client: TestClient):
    """Senha com menos de 8 caracteres deve ser rejeitada."""
    resposta = client.post("/auth/registrar", json={
        "nome_completo": "Pietro Nozella",
        "email": "fraco@fallsense.com",
        "telefone": "11999999999",
        "senha": "abc1"
    })
    assert resposta.status_code == 422


def test_registro_senha_sem_numero(client: TestClient):
    """Senha sem número deve ser rejeitada."""
    resposta = client.post("/auth/registrar", json={
        "nome_completo": "Pietro Nozella",
        "email": "fraco@fallsense.com",
        "telefone": "11999999999",
        "senha": "senhasemnum"
    })
    assert resposta.status_code == 422


# ---------------------------------------------------------------------------
# 2. Login
# ---------------------------------------------------------------------------

def test_login_primeira_etapa_retorna_requer_2fa(client: TestClient, usuario_registrado):
    """Login com senha correta sem 2FA deve retornar requer_2fa=True."""
    resposta = client.post("/auth/login", json={
        "email": "pietro@fallsense.com",
        "senha": "Senha123"
    })
    assert resposta.status_code == 200
    assert resposta.json()["requer_2fa"] is True


def test_login_completo_com_2fa(client: TestClient, usuario_registrado):
    """Login completo com senha + código TOTP válido deve retornar access_token."""
    totp_secret = usuario_registrado["totp_secret"]
    codigo = pyotp.TOTP(totp_secret).now()

    resposta = client.post("/auth/login", json={
        "email": "pietro@fallsense.com",
        "senha": "Senha123",
        "codigo_2fa": codigo
    })
    assert resposta.status_code == 200
    dados = resposta.json()
    assert "access_token" in dados
    assert dados["requer_2fa"] is False


def test_login_senha_incorreta(client: TestClient, usuario_registrado):
    """Senha errada deve retornar 400."""
    resposta = client.post("/auth/login", json={
        "email": "pietro@fallsense.com",
        "senha": "SenhaErrada1"
    })
    assert resposta.status_code == 400


def test_login_2fa_incorreto(client: TestClient, usuario_registrado):
    """Código 2FA inválido deve retornar 400."""
    resposta = client.post("/auth/login", json={
        "email": "pietro@fallsense.com",
        "senha": "Senha123",
        "codigo_2fa": "000000"
    })
    assert resposta.status_code == 400


# ---------------------------------------------------------------------------
# 3. Proteção contra força bruta (req. 1.11)
# ---------------------------------------------------------------------------

def test_bloqueio_por_forca_bruta(client: TestClient, usuario_registrado):
    """Após 3 tentativas com senha errada, a conta deve ser bloqueada (429)."""
    for _ in range(3):
        client.post("/auth/login", json={
            "email": "pietro@fallsense.com",
            "senha": "SenhaErrada1"
        })

    # A quarta tentativa (mesmo com senha certa) deve ser bloqueada
    resposta = client.post("/auth/login", json={
        "email": "pietro@fallsense.com",
        "senha": "Senha123"
    })
    assert resposta.status_code == 429


# ---------------------------------------------------------------------------
# 4. Logout e invalidação de sessão (req. 1.10)
# ---------------------------------------------------------------------------

def _fazer_login_completo(client: TestClient, usuario_registrado) -> str:
    """Helper: retorna o access_token após login completo com 2FA."""
    totp_secret = usuario_registrado["totp_secret"]
    codigo = pyotp.TOTP(totp_secret).now()
    resposta = client.post("/auth/login", json={
        "email": "pietro@fallsense.com",
        "senha": "Senha123",
        "codigo_2fa": codigo
    })
    return resposta.json()["access_token"]


def test_logout_sucesso(client: TestClient, usuario_registrado):
    """Logout com token válido deve retornar 200."""
    token = _fazer_login_completo(client, usuario_registrado)
    resposta = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 200


def test_token_revogado_apos_logout(client: TestClient, usuario_registrado):
    """Token usado no logout não deve ser aceito novamente (401)."""
    token = _fazer_login_completo(client, usuario_registrado)

    # Primeiro logout — deve funcionar
    client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})

    # Segunda tentativa com o mesmo token — deve ser rejeitada
    resposta = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 401


def test_logout_sem_token(client: TestClient):
    """Logout sem header Authorization deve retornar 422."""
    resposta = client.post("/auth/logout")
    assert resposta.status_code == 422
