import re
from pydantic import BaseModel, EmailStr, field_validator

# Validação do JSON do Swagger para Registro e Login
class RegistroPayload(BaseModel):
    nome_completo: str
    email: EmailStr
    telefone: str
    senha: str

    @field_validator("senha")
    @classmethod
    def validar_forca_senha(cls, v: str) -> str:
        # Mínimo 8 caracteres, ao menos uma letra e um número
        if len(v) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("A senha deve conter pelo menos uma letra.")
        if not re.search(r"\d", v):
            raise ValueError("A senha deve conter pelo menos um número.")
        return v

class LoginPayload(BaseModel):
    email: EmailStr
    senha: str
    codigo_2fa: str | None = None

# Validação do JSON do Swagger para Recuperação de Senha
class EsqueciSenhaPayload(BaseModel):
    email: EmailStr

class ResetarSenhaPayload(BaseModel):
    # Adicionamos o e-mail aqui também, caso o Flutter envie
    email: EmailStr | None = None 
    token: str
    # Usamos 'nova_senha' pois é o que está no seu recuperacao.py
    nova_senha: str