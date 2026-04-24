"""
Testes do fluxo de autenticação.
Cobre cadastro, login em duas etapas, bloqueio por tentativas inválidas e logout.
"""
import pyotp
from fastapi.testclient import TestClient

from models.user import PessoaMonitorada, Pulseira, User
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
    assert dados["totp_uri"].startswith("otpauth://totp/FallSense:pietro%40fallsense.com")
    assert f"secret={dados['totp_secret']}" in dados["totp_uri"]
    assert "issuer=FallSense" in dados["totp_uri"]
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
    dados = resposta.json()
    assert dados["requer_2fa"] is True
    assert "challenge_id" in dados
    assert dados["expires_in"] == 120


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


def test_login_completo_com_challenge_2fa(client: TestClient, usuario_registrado):
    """Segunda etapa com challenge_id não deve exigir reenviar a senha."""
    primeira_etapa = client.post("/auth/login", json={
        "email": "pietro@fallsense.com",
        "senha": "Senha123!"
    })
    assert primeira_etapa.status_code == 200

    challenge_id = primeira_etapa.json()["challenge_id"]
    codigo = pyotp.TOTP(usuario_registrado["totp_secret"]).now()

    resposta = client.post("/auth/login", json={
        "email": "pietro@fallsense.com",
        "challenge_id": challenge_id,
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


def test_atualizar_perfil_usuario_autenticado(client: TestClient, usuario_registrado):
    """PATCH /me deve atualizar dados cadastrais do usuario autenticado."""
    token = _fazer_login_completo(client, usuario_registrado)

    resposta = client.patch(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nome_completo": "Pietro Atualizado",
            "email": "pietro.novo@fallsense.com",
            "telefone": "11888888888",
        },
    )

    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["nome_completo"] == "Pietro Atualizado"
    assert dados["email"] == "pietro.novo@fallsense.com"
    assert dados["telefone"] == "11888888888"
    assert dados["access_token"]

    perfil = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {dados['access_token']}"},
    )
    assert perfil.status_code == 200
    assert perfil.json()["email"] == "pietro.novo@fallsense.com"


def test_atualizar_perfil_rejeita_email_duplicado(client: TestClient, usuario_registrado):
    """PATCH /me nao deve permitir usar e-mail de outro usuario."""
    client.post("/auth/registrar", json={
        "nome_completo": "Outro Usuario",
        "email": "outro@fallsense.com",
        "telefone": "11777777777",
        "senha": "Senha123!"
    })
    token = _fazer_login_completo(client, usuario_registrado)

    resposta = client.patch(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nome_completo": "Pietro Teste",
            "email": "outro@fallsense.com",
            "telefone": "11999999999",
        },
    )

    assert resposta.status_code == 400


def test_alterar_senha_usuario_autenticado(client: TestClient, usuario_registrado):
    """PATCH /me/senha deve trocar a senha do usuario autenticado."""
    token = _fazer_login_completo(client, usuario_registrado)

    resposta = client.patch(
        "/auth/me/senha",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "senha_atual": "Senha123!",
            "nova_senha": "NovaSenha123!",
        },
    )

    assert resposta.status_code == 200

    login_antigo = client.post("/auth/login", json={
        "email": "pietro@fallsense.com",
        "senha": "Senha123!",
    })
    assert login_antigo.status_code == 400

    login_novo = client.post("/auth/login", json={
        "email": "pietro@fallsense.com",
        "senha": "NovaSenha123!",
    })
    assert login_novo.status_code == 200
    assert login_novo.json()["requer_2fa"] is True


def test_alterar_senha_rejeita_senha_atual_incorreta(client: TestClient, usuario_registrado):
    """PATCH /me/senha deve validar a senha atual antes de salvar."""
    token = _fazer_login_completo(client, usuario_registrado)

    resposta = client.patch(
        "/auth/me/senha",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "senha_atual": "SenhaErrada123!",
            "nova_senha": "NovaSenha123!",
        },
    )

    assert resposta.status_code == 400


def test_alterar_senha_rejeita_senha_fraca(client: TestClient, usuario_registrado):
    """PATCH /me/senha deve reaproveitar a regra de forca da senha."""
    token = _fazer_login_completo(client, usuario_registrado)

    resposta = client.patch(
        "/auth/me/senha",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "senha_atual": "Senha123!",
            "nova_senha": "fraca",
        },
    )

    assert resposta.status_code == 422


def test_excluir_conta_usuario_autenticado(client: TestClient, usuario_registrado):
    """DELETE /me deve excluir o usuario e invalidar o token atual."""
    token = _fazer_login_completo(client, usuario_registrado)
    db = get_db_direto()
    usuario = db.query(User).filter(User.email == "pietro@fallsense.com").first()
    pessoa = PessoaMonitorada(
        usuario_responsavel_id=usuario.id,
        nome_completo="Pessoa Monitorada",
    )
    db.add(pessoa)
    db.commit()
    db.refresh(pessoa)
    db.add(Pulseira(
        mac_address="AA:BB:CC:DD:EE:01",
        pessoa_monitorada_id=pessoa.id,
        versao_firmware="1.0.0",
    ))
    db.commit()
    db.close()

    resposta = client.request(
        "DELETE",
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"senha": "Senha123!"},
    )

    assert resposta.status_code == 200

    perfil = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert perfil.status_code == 401

    login = client.post("/auth/login", json={
        "email": "pietro@fallsense.com",
        "senha": "Senha123!",
    })
    assert login.status_code == 400

    db = get_db_direto()
    usuario = db.query(User).filter(User.email == "pietro@fallsense.com").first()
    pessoa = db.query(PessoaMonitorada).filter(
        PessoaMonitorada.nome_completo == "Pessoa Monitorada"
    ).first()
    pulseira = db.query(Pulseira).filter(
        Pulseira.mac_address == "AA:BB:CC:DD:EE:01"
    ).first()
    db.close()
    assert usuario is None
    assert pessoa is None
    assert pulseira is not None
    assert pulseira.pessoa_monitorada_id is None


def test_excluir_conta_rejeita_senha_incorreta(client: TestClient, usuario_registrado):
    """DELETE /me nao deve excluir conta quando a senha estiver incorreta."""
    token = _fazer_login_completo(client, usuario_registrado)

    resposta = client.request(
        "DELETE",
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"senha": "SenhaErrada123!"},
    )

    assert resposta.status_code == 400

    perfil = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert perfil.status_code == 200
