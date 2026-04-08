import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Carrega o arquivo `.env` a partir da raiz do Backend para disponibilizar a
# chave usada nas rotinas de criptografia.
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)

# Recupera a chave mestra que será usada para cifrar e decifrar os dados.
SECRET_KEY = os.getenv("ENCRYPTION_KEY")

# Sem a chave de criptografia, o sistema não consegue proteger nem abrir os
# dados sensíveis; por isso a inicialização é interrompida imediatamente.
if not SECRET_KEY:
    print("\n[ERRO] Cade a ENCRYPTION_KEY no .env? Arruma aí!")
    raise SystemExit("Sistema parado por falta de chave de segurança.")

# Instancia o mecanismo de criptografia simétrica usado em todo o módulo.
fernet = Fernet(SECRET_KEY.encode())

def proteger_dado(texto_limpo: str) -> str:
    """Criptografa um texto antes de persistir o valor em banco."""
    if not texto_limpo:
        return None
    # O valor é convertido para ciphertext para que o conteúdo original não
    # fique legível fora do processo autorizado de descriptografia.
    return fernet.encrypt(texto_limpo.encode()).decode()

def abrir_dado(texto_criptografado: str) -> str:
    """Descriptografa um valor previamente protegido para uso interno da aplicação."""
    if not texto_criptografado:
        return None
    # A operação inversa devolve o conteúdo original usando a mesma chave mestra.
    return fernet.decrypt(texto_criptografado.encode()).decode()
