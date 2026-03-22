"""
Testes de recuperação de senha — cobre requisitos 2.1 a 2.7 do checklist de segurança.
Envio de e-mail é simulado (mock) para não depender de SMTP real.
"""
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models.user import TokenRecuperacao, LogAuditoria
from tests.conftest import get_db_direto


# ---------------------------------------------------------------------------
# 2.1 / 2.2 / 2.3 — Solicitação de recuperação
# ---------------------------------------------------------------------------

@patch("routers.recuperacao.FastMail.send_message", new_callable=AsyncMock)
def test_esqueci_senha_usuario_existente(mock_mail, client: TestClient, usuario_registrado):
    """Solicitação para e-mail cadastrado deve gerar token e retornar 200."""
    resposta = client.post("/auth/esqueci-senha", json={"email": "pietro@fallsense.com"})
    assert resposta.status_code == 200
    assert mock_mail.called

    # Verifica que o token foi persistido no banco
    db = get_db_direto()
    token = db.query(TokenRecuperacao).filter(
        TokenRecuperacao.email == "pietro@fallsense.com"
    ).first()
    db.close()

    assert token is not None
    assert token.usado is False
    assert token.expiracao > datetime.utcnow()


@patch("routers.recuperacao.FastMail.send_message", new_callable=AsyncMock)
def test_esqueci_senha_email_inexistente_resposta_generica(mock_mail, client: TestClient):
    """E-mail não cadastrado deve retornar resposta genérica (não vazar informação)."""
    resposta = client.post("/auth/esqueci-senha", json={"email": "naoexiste@fallsense.com"})
    assert resposta.status_code == 200
    # Resposta deve ser genérica — não deve confirmar se o e-mail existe
    assert "cadastrado" in resposta.json()["mensagem"].lower() or \
           "enviado" in resposta.json()["mensagem"].lower()
    assert not mock_mail.called


# ---------------------------------------------------------------------------
# 2.4 / 2.5 — Reset de senha
# ---------------------------------------------------------------------------

@patch("routers.recuperacao.FastMail.send_message", new_callable=AsyncMock)
def test_resetar_senha_token_valido(mock_mail, client: TestClient, usuario_registrado):
    """Reset com token válido deve atualizar a senha e retornar 200."""
    client.post("/auth/esqueci-senha", json={"email": "pietro@fallsense.com"})

    db = get_db_direto()
    token = db.query(TokenRecuperacao).filter(
        TokenRecuperacao.email == "pietro@fallsense.com"
    ).first()
    token_valor = token.token
    db.close()

    resposta = client.post("/auth/resetar-senha", json={
        "token": token_valor,
        "nova_senha": "NovaSenha456"
    })
    assert resposta.status_code == 200

    # Verifica que o token foi marcado como usado (req. 2.4)
    db = get_db_direto()
    token_atualizado = db.query(TokenRecuperacao).filter(
        TokenRecuperacao.token == token_valor
    ).first()
    db.close()
    assert token_atualizado.usado is True


@patch("routers.recuperacao.FastMail.send_message", new_callable=AsyncMock)
def test_resetar_senha_token_ja_usado(mock_mail, client: TestClient, usuario_registrado):
    """Reutilização do mesmo token deve ser rejeitada com 400 (req. 2.4)."""
    client.post("/auth/esqueci-senha", json={"email": "pietro@fallsense.com"})

    db = get_db_direto()
    token_valor = db.query(TokenRecuperacao).filter(
        TokenRecuperacao.email == "pietro@fallsense.com"
    ).first().token
    db.close()

    # Primeiro reset — deve funcionar
    client.post("/auth/resetar-senha", json={"token": token_valor, "nova_senha": "NovaSenha456"})

    # Segundo reset com o mesmo token — deve ser rejeitado
    resposta = client.post("/auth/resetar-senha", json={"token": token_valor, "nova_senha": "OutraSenha789"})
    assert resposta.status_code == 400


def test_resetar_senha_token_expirado(client: TestClient, usuario_registrado):
    """Token expirado deve retornar 400 (req. 2.5)."""
    # Insere diretamente um token já expirado no banco
    db = get_db_direto()
    from models.user import User
    usuario = db.query(User).filter(User.email == "pietro@fallsense.com").first()
    db.add(TokenRecuperacao(
        email="pietro@fallsense.com",
        token="token-expirado-simulado",
        expiracao=datetime.utcnow() - timedelta(minutes=30),  # expirado há 30 min
        usado=False
    ))
    db.commit()
    db.close()

    resposta = client.post("/auth/resetar-senha", json={
        "token": "token-expirado-simulado",
        "nova_senha": "NovaSenha456"
    })
    assert resposta.status_code == 400


def test_resetar_senha_token_inexistente(client: TestClient, usuario_registrado):
    """Token que não existe no banco deve retornar 400."""
    resposta = client.post("/auth/resetar-senha", json={
        "token": "token-que-nao-existe",
        "nova_senha": "NovaSenha456"
    })
    assert resposta.status_code == 400


# ---------------------------------------------------------------------------
# 2.6 / 2.7 — Logs de auditoria
# ---------------------------------------------------------------------------

@patch("routers.recuperacao.FastMail.send_message", new_callable=AsyncMock)
def test_log_gerado_na_solicitacao(mock_mail, client: TestClient, usuario_registrado):
    """Solicitação de recuperação deve gerar entrada em LogAuditoria (req. 2.6)."""
    client.post("/auth/esqueci-senha", json={"email": "pietro@fallsense.com"})

    db = get_db_direto()
    log = db.query(LogAuditoria).filter(
        LogAuditoria.acao == "RECUPERACAO_SENHA_SOLICITADA"
    ).first()
    db.close()

    assert log is not None
    assert log.status == "SUCESSO"


@patch("routers.recuperacao.FastMail.send_message", new_callable=AsyncMock)
def test_log_gerado_no_reset(mock_mail, client: TestClient, usuario_registrado):
    """Reset bem-sucedido deve gerar entrada em LogAuditoria (req. 2.7)."""
    client.post("/auth/esqueci-senha", json={"email": "pietro@fallsense.com"})

    db = get_db_direto()
    token_valor = db.query(TokenRecuperacao).filter(
        TokenRecuperacao.email == "pietro@fallsense.com"
    ).first().token
    db.close()

    client.post("/auth/resetar-senha", json={"token": token_valor, "nova_senha": "NovaSenha456"})

    db = get_db_direto()
    log = db.query(LogAuditoria).filter(
        LogAuditoria.acao == "RECUPERACAO_SENHA_RESET",
        LogAuditoria.status == "SUCESSO"
    ).first()
    db.close()

    assert log is not None
