from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

# caminho para p python achar o .env na pasta do beckend, mesmo estando 
# na pasta security. 
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)

# chave do arquivo .env
SECRET_KEY = os.getenv("ENCRYPTION_KEY")

if not SECRET_KEY:
    # evita rodar sem egurança.
    raise ValueError("ERRO CRÍTICO: ENCRYPTION_KEY não encontrada no .env!")

# Preparando o motor Fernet (AES-256)
fernet = Fernet(SECRET_KEY.encode())

def proteger_dado(texto_limpo: str) -> str:
    """Transforma o segredo em código AES-256 para o Supabase"""
    if not texto_limpo:
        return None
    # Encripta os bytes e decodifica para string para salvar no banco
    return fernet.encrypt(texto_limpo.encode()).decode()

def abrir_dado(texto_criptografado: str) -> str:
    """Transforma o código do Supabase de volta em texto original"""
    if not texto_criptografado:
        return None
    # Descriptografa o código usando a chave mestra
    return fernet.decrypt(texto_criptografado.encode()).decode()