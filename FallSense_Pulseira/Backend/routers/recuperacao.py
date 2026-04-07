import os
import secrets
import sys
import requests
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
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

# Função via Brevo API
def enviar_email_brevo(destinatario: str, token: str):
    url = "https://api.brevo.com/v3/smtp/email"
    
    # A Chave que pegamos no Brevo e colocamos no Render vai entrar aqui
    headers = {
        "accept": "application/json",
        "api-key": os.getenv("BREVO_API_KEY"),
        "content-type": "application/json"
    }
    
    corpo_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 8px; border: 1px solid #ddd;">
                <h2 style="color: #2196F3; text-align: center;">Segurança FallSense</h2>
                <p>Olá,</p>
                <p>Você solicitou a recuperação de senha para a <strong>Pulseira Sensorial FallSense</strong>.</p>
                <p>Seu código de verificação é:</p>
                <div style="background: #e3f2fd; padding: 15px; font-size: 24px; font-family: monospace; font-weight: bold; border: 2px dashed #2196F3; text-align: center; color: #1976D2;">
                    {token}
                </div>
                <p style="font-size: 13px; color: #666;">Este código é válido por 15 minutos. Se você não solicitou isso, ignore este e-mail.</p>
            </div>
        </body>
    </html>
    """
    
    payload = {
        "sender": {"name": "Suporte FallSense", "email": "suporte.fallsense@gmail.com"},
        "to": [{"email": destinatario}],
        "subject": "Código de Recuperação - FallSense",
        "htmlContent": corpo_html
    }
    
    try:
        resposta = requests.post(url, json=payload, headers=headers)
        # Esse print vai fofocar no log do Render se o Brevo aceitou ou não
        print(f"📢 STATUS BREVO: {resposta.status_code} - {resposta.text}")
    except Exception as e:
        print(f"🚨 ERRO HTTP (BREVO): {str(e)}")


@router.post("/esqueci-senha")
async def solicitar_recuperacao(
    payload: EsqueciSenhaPayload, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    usuario = db.query(User).filter(User.email == payload.email).first()
    
    if not usuario:
        return {"mensagem": "Se o e-mail estiver cadastrado, o código será enviado."}

    # Gerar código numérico de 6 dígitos
    token_gerado = "".join(secrets.choice("0123456789") for _ in range(6))
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=15)

    novo_token = TokenRecuperacao(
        email=payload.email,
        token=token_gerado,
        usado=False,
        expiracao=expiracao
    )
    db.add(novo_token)
    db.commit()

    # DISPARA O E-MAIL VIA BREVO EM SEGUNDO PLANO
    background_tasks.add_task(enviar_email_brevo, payload.email, token_gerado)

    db.add(LogAuditoria(
        usuario_id=usuario.id,
        acao="RECUPERACAO_SENHA_SOLICITADA",
        descricao=f"Código gerado e enviado via Brevo API para {payload.email}.",
        status="SUCESSO"
    ))
    db.commit()

    return {"mensagem": "E-mail enviado com sucesso!"}

@router.post("/resetar-senha")
def resetar_senha(payload: ResetarSenhaPayload, db: Session = Depends(get_db)):
    db_token = db.query(TokenRecuperacao).filter(
        TokenRecuperacao.token == payload.token,
        TokenRecuperacao.usado == False
    ).first()

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
