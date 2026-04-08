import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.orm import Session

load_dotenv()

# Lê a chave secreta usada para assinar e validar os JWTs da aplicação.
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
TEMPO_EXPIRACAO_MINUTOS = 60  # O token dura 1 hora

# Sem a chave JWT, a aplicação não consegue emitir nem verificar tokens com
# segurança; por isso a inicialização é interrompida.
if not SECRET_KEY:
    raise ValueError("⚠️ ALERTA: A variável JWT_SECRET não foi encontrada no arquivo .env!")


# Gera um token assinado contendo a identidade do usuário e o prazo de expiração.
def criar_token_jwt(email: str) -> str:
    expiracao = datetime.utcnow() + timedelta(minutes=TEMPO_EXPIRACAO_MINUTOS)

    payload = {
        "sub": email,       # Identifica o dono do token.
        "exp": expiracao    # Define até quando o token será aceito.
    }

    # O JWT final é assinado com a chave secreta para impedir adulteração.
    token_codificado = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token_codificado


def verificar_token_jwt(token: str, db: Session) -> str:
    """Valida o JWT e retorna o e-mail associado ao token."""
    from models.user import TokenRevogado  # import local para evitar ciclo

    # Antes de validar o conteúdo do JWT, confirmamos se ele não foi revogado
    # manualmente no logout.
    if db.query(TokenRevogado).filter(TokenRevogado.token == token).first():
        raise HTTPException(status_code=401, detail="Token revogado. Faça login novamente.")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        # Sem o campo "sub", o token até pode existir tecnicamente, mas não
        # carrega a identidade necessária para autenticar a requisição.
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido.")
        return email
    except jwt.ExpiredSignatureError:
        # O token foi assinado corretamente, mas passou do prazo de validade.
        raise HTTPException(status_code=401, detail="Token expirado.")
    except jwt.InvalidTokenError:
        # Captura tokens adulterados, malformados ou assinados com chave incorreta.
        raise HTTPException(status_code=401, detail="Token inválido.")


def revogar_token(token: str, db: Session) -> None:
    """Registra o token na blacklist para impedir reutilização futura."""
    from models.user import TokenRevogado

    # A revogação mantém o token inválido mesmo antes da expiração natural.
    db.add(TokenRevogado(token=token))
    db.commit()
