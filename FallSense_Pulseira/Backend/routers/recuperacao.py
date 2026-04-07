import os
import secrets
import sys
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
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

# Confug para ambiente em nuvem
conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    # Converte para inteiro para evitar erro de tipo no SMTP
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER = os.getenv("MAIL_SERVER"),
    # Lê da nuvwm e converte String para Booleano real
    MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "True") == "True",
    MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", "False") == "True",
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
    TIMEOUT = 15
)

@router.post("/esqueci-senha")
async def solicitar_recuperacao(
    payload: EsqueciSenhaPayload, 
    background_tasks: BackgroundTasks, # Adicionado para não travar o app Flutter
    db: Session = Depends(get_db)
):
    usuario = db.query(User).filter(User.email == payload.email).first()
    
    if not usuario:
        # Resposta genérica por segurança (impede descoberta de e-mails)
        return {"mensagem": "Se o e-mail estiver cadastrado, o código será enviado."}

    # Gerar código numérico de 6 dígitos (Melhor UX para o usuário digitar no Flutter)
    token_gerado = "".join(secrets.choice("0123456789") for _ in range(6))
    
    # Uso de timezone.utc para evitar avisos de depreciação do Python
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=15)

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
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 8px; border: 1px solid #ddd;">
                <h2 style="color: #2196F3; text-align: center;">Segurança FallSense</h2>
                <p>Olá,</p>
                <p>Você solicitou a recuperação de senha para a <strong>Pulseira Sensorial FallSense</strong>.</p>
                <p>Seu código de verificação é:</p>
                <div style="background: #e3f2fd; padding: 15px; font-size: 24px; font-family: monospace; font-weight: bold; border: 2px dashed #2196F3; text-align: center; color: #1976D2;">
                    {token_gerado}
                </div>
                <p style="font-size: 13px; color: #666;">Este código é válido por 15 minutos. Se você não solicitou isso, ignore este e-mail.</p>
            </div>
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
        # Envia em segundo plano para liberar o Flutter imediatamente
        background_tasks.add_task(fm.send_message, message)

        db.add(LogAuditoria(
            usuario_id=usuario.id,
            acao="RECUPERACAO_SENHA_SOLICITADA",
            descricao=f"Código gerado e e-mail disparado para {payload.email}.",
            status="SUCESSO"
        ))
        db.commit()

        return {"mensagem": "E-mail enviado com sucesso!"}
        
    except Exception as e:
        # LOG DE CONSOLE: Isso vai mostrar o erro real no Dashboard do Render!
        print(f"ERRO NO ENVIO DE EMAIL: {str(e)}")
        
        db.add(LogAuditoria(
            usuario_id=usuario.id,
            acao="RECUPERACAO_SENHA_SOLICITADA",
            descricao=f"Falha ao enviar e-mail: {str(e)}",
            status="FALHA"
        ))
        db.commit()
        raise HTTPException(status_code=500, detail="Erro interno ao processar e-mail.")

@router.post("/resetar-senha")
def resetar_senha(payload: ResetarSenhaPayload, db: Session = Depends(get_db)):
    db_token = db.query(TokenRecuperacao).filter(
        TokenRecuperacao.token == payload.token,
        TokenRecuperacao.usado == False
    ).first()

    # Ajuste na comparação de data com timezone
    agora = datetime.now(timezone.utc)
    if not db_token or db_token.expiracao.replace(tzinfo=timezone.utc) < agora:
        db.add(LogAuditoria(
            usuario_id=None,
            acao="RECUPERACAO_SENHA_RESET",
            descricao="Tentativa de reset com código inválido/expirado.",
            status="FALHA"
        ))
        db.commit()
        raise HTTPException(status_code=400, detail="Código inválido ou expirado.")

    usuario = db.query(User).filter(User.email == db_token.email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    usuario.hashed_password = gerar_hash(payload.nova_senha)
    db_token.usado = True

    db.add(LogAuditoria(
        usuario_id=usuario.id,
        acao="RECUPERACAO_SENHA_RESET",
        descricao=f"Senha redefinida com sucesso para {usuario.email}.",
        status="SUCESSO"
    ))
    db.commit()

    return {"mensagem": "Senha atualizada com sucesso!"}
