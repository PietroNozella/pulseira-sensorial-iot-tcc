import os
import secrets
import sys
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from dotenv import load_dotenv

# Garante que o Python encontre as pastas na raiz do Backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- IMPORTS ALINHADOS COM SUA ESTRUTURA ---
from security.database import get_db
from security.hashing import gerar_hash
from models.user import User, TokenRecuperacao, LogAuditoria
from schemas.auth_schemas import EsqueciSenhaPayload, ResetarSenhaPayload

load_dotenv()
router = APIRouter()

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER = os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    TIMEOUT = 10
)

@router.post("/esqueci-senha")
async def solicitar_recuperacao(payload: EsqueciSenhaPayload, db: Session = Depends(get_db)):
    # Busca o usuário pelo e-mail
    usuario = db.query(User).filter(User.email == payload.email).first()
    
    if not usuario:
        return {"mensagem": "Se o e-mail estiver cadastrado, o código será enviado."}

    # Gera o Token e define expiração (15 min)
    token_gerado = secrets.token_urlsafe(32)
    expiracao = datetime.utcnow() + timedelta(minutes=15)

    # Salva no banco
    novo_token = TokenRecuperacao(
        email=payload.email,
        token=token_gerado,
        usado=False,
        expiracao=expiracao
    )
    db.add(novo_token)
    db.commit()

    corpo_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #2196F3;">Recuperação de Senha - FallSense</h2>
            <p>Olá,</p>
            <p>Seu código de segurança para a <strong>Pulseira Sensorial</strong> é:</p>
            <div style="background: #f4f4f4; padding: 15px; font-size: 20px; font-family: monospace; border: 1px dashed #2196F3; display: inline-block;">
                {token_gerado}
            </div>
            <p>Este código expira em 15 minutos.</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject="Código de Recuperação - FallSense",
        recipients=[payload.email],
        body=corpo_html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)

        # Registra a solicitação bem-sucedida no log de auditoria (req. 2.6)
        db.add(LogAuditoria(
            usuario_id=usuario.id,
            acao="RECUPERACAO_SENHA_SOLICITADA",
            descricao="Token de recuperação gerado e e-mail enviado para {}.".format(payload.email),
            status="SUCESSO"
        ))
        db.commit()

        return {"mensagem": "E-mail enviado com sucesso!"}
    except Exception as e:
        # Registra a falha no log de auditoria antes de lançar o erro (req. 2.6)
        db.add(LogAuditoria(
            usuario_id=usuario.id,
            acao="RECUPERACAO_SENHA_SOLICITADA",
            descricao="Falha ao enviar e-mail de recuperação para {}: {}.".format(payload.email, str(e)),
            status="FALHA"
        ))
        db.commit()

        raise HTTPException(status_code=500, detail="Erro ao enviar e-mail.")

@router.post("/resetar-senha")
def resetar_senha(payload: ResetarSenhaPayload, db: Session = Depends(get_db)):
    # Busca o token válido
    db_token = db.query(TokenRecuperacao).filter(
        TokenRecuperacao.token == payload.token,
        TokenRecuperacao.usado == False
    ).first()

    if not db_token or db_token.expiracao < datetime.utcnow():
        # Registra a tentativa com token inválido ou expirado (req. 2.7)
        db.add(LogAuditoria(
            usuario_id=None,
            acao="RECUPERACAO_SENHA_RESET",
            descricao="Tentativa de reset com token inválido ou expirado para o e-mail {}.".format(payload.token[:8] + "..."),
            status="FALHA"
        ))
        db.commit()
        raise HTTPException(status_code=400, detail="Token inválido ou expirado.")

    usuario = db.query(User).filter(User.email == db_token.email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    # Gera o hash da nova senha antes de salvar (nunca armazenar texto plano)
    usuario.hashed_password = gerar_hash(payload.nova_senha)
    db_token.usado = True

    # Registra o sucesso do reset no log de auditoria (req. 2.7)
    db.add(LogAuditoria(
        usuario_id=usuario.id,
        acao="RECUPERACAO_SENHA_RESET",
        descricao="Senha redefinida com sucesso para o usuário {}.".format(usuario.email),
        status="SUCESSO"
    ))
    db.commit()

    return {"mensagem": "Senha atualizada com sucesso!"}