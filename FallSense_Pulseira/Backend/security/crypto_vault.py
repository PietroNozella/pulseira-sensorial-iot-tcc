import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# --- CONFIGURAÇÃO DO AMBIENTE (REQ 3.6) ---
# Aqui eu busco o arquivo .env que tá na raiz do projeto
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)

# Pego a chave mestra que a gente salvou no .env
SECRET_KEY = os.getenv("ENCRYPTION_KEY")

# Trava de segurança: se a chave não estiver no .env, o sistema nem abre
if not SECRET_KEY:
    print("\n[ERRO] Cade a ENCRYPTION_KEY no .env? Arruma aí!")
    raise SystemExit("Sistema parado por falta de chave de segurança.")

# Inicializo o motor de criptografia (AES-256)
fernet = Fernet(SECRET_KEY.encode())

def proteger_dado(texto_limpo: str) -> str:
    """ REQ 3.4: Criptografa o dado antes de salvar no banco """
    if not texto_limpo:
        return None
    # Transforma o texto em "sopa de letras" (Ciphertext)
    return fernet.encrypt(texto_limpo.encode()).decode()

def abrir_dado(texto_criptografado: str) -> str:
    """ REQ 3.5: Abre o dado que veio do banco pra gente ler """
    if not texto_criptografado:
        return None
    # Devolve o texto original usando a chave mestra
    return fernet.decrypt(texto_criptografado.encode()).decode()