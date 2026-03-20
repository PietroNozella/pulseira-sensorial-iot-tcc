from pydantic import BaseModel, EmailStr

# Validação do JSON do Swagger para Registro e Login
class RegistroPayload(BaseModel):
    nome_completo: str
    email: EmailStr
    telefone: str
    senha: str

class LoginPayload(BaseModel):
    email: EmailStr
    senha: str
    codigo_2fa: str | None = None

# Validação do JSON do Swagger para Recuperação de Senha
class EsqueciSenhaPayload(BaseModel):
    email: EmailStr

class ResetarSenhaPayload(BaseModel):
    token: str
    nova_senha: str