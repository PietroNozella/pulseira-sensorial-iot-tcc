"""
Testes do fluxo de autenticação.
Cobre cadastro, login em duas etapas, bloqueio por tentativas inválidas e logout.
"""
import pyotp
from fastapi.testclient import TestClient

from models.user import User
from tests.conftest import get_db_direto


# ---------------------------------------------------------------------------
# 1. Registro
# ---------------------------------------------------------------------------

def test_registro_sucesso(client: TestClient):
    """Usuário válido deve ser registrado com status 201."""
    resposta = client.post("/auth/registrar", json={
        "nome_completo": "Pietro Nozella",
        "email": "pietro@fallsense.com",
        "telefone": "11999999999",
        "senha": "Senha123!"
    })
    assert resposta.status_code == 201
    dados = resposta.json()
    # Esses dados sensíveis só devem aparecer no momento do cadastro inicial.
    assert "totp_secret" in dados
    assert "recovery_codes" in dados
    assert len(dados["recovery_codes"]) == 8


def test_registro_persiste_nome_e_telefone(client: TestClient):
    """Cadastro deve persistir nome completo e telefone em usuarios_api."""
    resposta = client.post("/auth/registrar", json={
        "nome_completo": "Pietro Nozella",
        "email": "pietro@fallsense.com",
        "telefone": "11999999999",
        "senha": "Senha123!"
    })
    assert resposta.status_code == 201

    db = get_db_direto()
    usuario = db.query(User).filter(User.email == "pietro@fallsense.com").first()
    db.close()

    assert usuario is not None
    assert usuario.nome_completo == "Pietro Nozella"
    assert usuario.telefone == "11999999999"


def test_registro_email_duplicado(client: TestClient, usuario_registrado):
    """Segundo cadastro com o mesmo e-mail deve retornar 400."""
    resposta = client.post("/auth/registrar", json={
        "nome_completo": "Pietro Nozella",
        "email": "pietro@fallsense.com",
        "telefone": "11999999999",
        "senha": "Senha123!"
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
        "senha": "Senha123!"
    })
    assert resposta.status_code == 200
    assert resposta.json()["requer_2fa"] is True


def test_login_completo_com_2fa(client: TestClient, usuario_registrado):
    """Login completo com senha + código TOTP válido deve retornar access_token."""
    totp_secret = usuario_registrado["totp_secret"]
    codigo = pyotp.TOTP(totp_secret).now()

    resposta = client.post("/auth/login", json={
        "email": "pietro@fallsense.com",
        "senha": "Senha123!",
        "codigo_2fa": codigo
    })
    assert resposta.status_code == 200
    dados = resposta.json()
    assert "access_token" in dados
    assert dados["nome_completo"] == "Pietro Teste"
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
        "senha": "Senha123!",
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

    # Depois do limite de falhas, até uma tentativa com a senha correta deve
    # ser barrada enquanto o bloqueio estiver ativo.
    resposta = client.post("/auth/login", json={
        "email": "pietro@fallsense.com",
        "senha": "Senha123!"
    })
    assert resposta.status_code == 429


# ---------------------------------------------------------------------------
# 4. Logout e invalidação de sessão (req. 1.10)
# ---------------------------------------------------------------------------

def _fazer_login_completo(client: TestClient, usuario_registrado) -> str:
    """Executa o login completo e devolve um token pronto para testes autenticados."""
    totp_secret = usuario_registrado["totp_secret"]
    codigo = pyotp.TOTP(totp_secret).now()
    resposta = client.post("/auth/login", json={
        "email": "pietro@fallsense.com",
        "senha": "Senha123!",
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

    # A primeira chamada invalida o token e encerra a sessão normalmente.
    client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})

    # A segunda chamada prova que o token foi realmente revogado.
    resposta = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 401


def test_logout_sem_token(client: TestClient):
    """Logout sem header Authorization deve retornar 422."""
    resposta = client.post("/auth/logout")
    assert resposta.status_code == 422


def test_obter_perfil_usuario_autenticado(client: TestClient, usuario_registrado):
    """Endpoint /me deve retornar os dados persistidos do usuário autenticado."""
    token = _fazer_login_completo(client, usuario_registrado)

    resposta = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 200

    dados = resposta.json()
    assert dados["nome_completo"] == "Pietro Teste"
    assert dados["email"] == "pietro@fallsense.com"
    assert dados["telefone"] == "11999999999"
