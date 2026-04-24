import pyotp

def gerar_segredo_totp() -> str:
    # Cria o segredo compartilhado que será cadastrado no aplicativo
    # autenticador do usuário para gerar os códigos temporários.
    return pyotp.random_base32()

def gerar_uri_totp(segredo: str, email: str) -> str:
    totp = pyotp.TOTP(segredo)
    return totp.provisioning_uri(name=email, issuer_name="FallSense")

def verificar_totp(segredo: str, codigo_digitado: str) -> bool:
    # Reconstrói o gerador TOTP a partir do segredo salvo e valida o código
    # informado no momento do login.
    totp = pyotp.TOTP(segredo)
    return totp.verify(codigo_digitado)
