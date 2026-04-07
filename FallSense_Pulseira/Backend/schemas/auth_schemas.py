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
        #frase de erro
        msg_erro = "A senha deve conter pelo menos letras, números e um caractere especial."

        # Mínimo 8 caracteres E ter letra E ter número E ter caractere especial
        tem_o_tamanho = len(v) >= 8
        tem_letra = re.search(r"[A-Za-z]", v)
        tem_numero = re.search(r"\d", v)
        tem_especial = re.search(r"[!@#$%^&*(),.?\":{}|<>]", v)

        # Se faltar QUALQUER um desses, ele manda a sua frase
        if not (tem_o_tamanho and tem_letra and tem_numero and tem_especial):
            raise ValueError(msg_erro)
            
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