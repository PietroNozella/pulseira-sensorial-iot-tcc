import re
from pydantic import BaseModel, EmailStr, field_validator

# Schema recebido no cadastro. Ele define o formato esperado pela API e aplica
# as regras mínimas de validação antes de a senha seguir para hash.
class RegistroPayload(BaseModel):
    nome_completo: str
    email: EmailStr
    telefone: str
    senha: str

    @field_validator("senha")
    @classmethod
    def validar_forca_senha(cls, v: str) -> str:
        # Mantemos uma mensagem única para que o cliente receba um retorno
        # simples quando a senha não atender aos critérios mínimos.
        msg_erro = "A senha deve conter pelo menos letras, números e um caractere especial."

        # Cada verificação cobre um requisito diferente de complexidade.
        tem_o_tamanho = len(v) >= 8
        tem_letra = re.search(r"[A-Za-z]", v)
        tem_numero = re.search(r"\d", v)
        tem_especial = re.search(r"[!@#$%^&*(),.?\":{}|<>]", v)

        # Se qualquer um dos critérios falhar, a senha é rejeitada ainda na
        # validação do schema.
        if not (tem_o_tamanho and tem_letra and tem_numero and tem_especial):
            raise ValueError(msg_erro)
            
        return v

# Payload usado no login. O código 2FA é opcional porque a autenticação pode
# acontecer em duas etapas: senha primeiro e token do autenticador depois.
class LoginPayload(BaseModel):
    email: EmailStr
    senha: str
    codigo_2fa: str | None = None

# Payload mínimo para iniciar o fluxo de recuperação de senha.
class EsqueciSenhaPayload(BaseModel):
    email: EmailStr

# Dados necessários para concluir a redefinição da senha com o token enviado.
class ResetarSenhaPayload(BaseModel):
    # O e-mail é opcional porque o backend consegue localizar a solicitação
    # principalmente pelo token, mas o cliente ainda pode enviar esse campo.
    email: EmailStr | None = None 
    token: str
    # O nome do campo permanece alinhado com o que a rota de recuperação espera.
    nova_senha: str


class PerfilResponse(BaseModel):
    nome_completo: str | None = None
    email: EmailStr
    telefone: str | None = None


class PessoaMonitoradaPayload(BaseModel):
    nome_completo: str


class PessoaMonitoradaResponse(BaseModel):
    id: int
    nome_completo: str | None = None
