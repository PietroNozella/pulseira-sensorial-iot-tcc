import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Puxa a chave secreta do cofre
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
TEMPO_EXPIRACAO_MINUTOS = 60 # O token dura 1 hora

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