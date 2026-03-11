# backend/security/totp_handler.py
import pyotp

def gerar_segredo_totp() -> str:
    # Gera uma chave secreta única de 32 caracteres para o Google Authenticator do usuário
    return pyotp.random_base32()

def verificar_totp(segredo: str, codigo_digitado: str) -> bool:
    # Verifica se o código de 6 dígitos digitado pelo idoso/cuidador está correto
    totp = pyotp.TOTP(segredo)
    return totp.verify(codigo_digitado)