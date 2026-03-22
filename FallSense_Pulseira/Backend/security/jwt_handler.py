import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.orm import Session

load_dotenv()

# Puxa a chave secreta do cofre
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
TEMPO_EXPIRACAO_MINUTOS = 60  # O token dura 1 hora

# Trava de segurança: impede iniciar o servidor sem a chave JWT configurada
if not SECRET_KEY:
    raise ValueError("⚠️ ALERTA: A variável JWT_SECRET não foi encontrada no arquivo .env!")


# Gerar um JWT assinado criptograficamente com o e-mail do usuário
def criar_token_jwt(email: str) -> str:
    expiracao = datetime.utcnow() + timedelta(minutes=TEMPO_EXPIRACAO_MINUTOS)

    payload = {
        "sub": email,       # 'sub' (subject) é o dono do token
        "exp": expiracao    # 'exp' é quando o token perde a validade
    }

    # Fabricar o token juntando os dados com a sua chave secreta
    token_codificado = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token_codificado


def verificar_token_jwt(token: str, db: Session) -> str:
    """Valida assinatura e expiração do JWT e garante que não foi revogado."""
    from models.user import TokenRevogado  # import local para evitar ciclo

    # Rejeita imediatamente se o token estiver na blacklist
    if db.query(TokenRevogado).filter(TokenRevogado.token == token).first():
        raise HTTPException(status_code=401, detail="Token revogado. Faça login novamente.")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido.")
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido.")


def revogar_token(token: str, db: Session) -> None:
    """Adiciona o token à blacklist de revogados."""
    from models.user import TokenRevogado

    # Salva o token na tabela de revogados para bloquear reuso
    db.add(TokenRevogado(token=token))
    db.commit()
