from datetime import datetime
import re
from pydantic import BaseModel, EmailStr, field_validator


def validar_forca_senha(valor: str) -> str:
    msg_erro = "A senha deve conter pelo menos letras, números e um caractere especial."

    tem_o_tamanho = len(valor) >= 8
    tem_letra = re.search(r"[A-Za-z]", valor)
    tem_numero = re.search(r"\d", valor)
    tem_especial = re.search(r"[!@#$%^&*(),.?\":{}|<>]", valor)

    if not (tem_o_tamanho and tem_letra and tem_numero and tem_especial):
        raise ValueError(msg_erro)

    return valor


# Schema recebido no cadastro. Ele define o formato esperado pela API e aplica
# as regras mínimas de validação antes de a senha seguir para hash.
class RegistroPayload(BaseModel):
    nome_completo: str
    email: EmailStr
    telefone: str
    senha: str
    termos_aceitos: bool

    @field_validator("senha")
    @classmethod
    def validar_forca_senha(cls, v: str) -> str:
        return validar_forca_senha(v)

# Payload usado no login. O código 2FA é opcional porque a autenticação pode
# acontecer em duas etapas: senha primeiro e token do autenticador depois.
class LoginPayload(BaseModel):
    email: EmailStr
    senha: str | None = None
    codigo_2fa: str | None = None
    challenge_id: str | None = None

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


class PerfilUpdatePayload(BaseModel):
    nome_completo: str
    email: EmailStr
    telefone: str | None = None


class PerfilAtualizadoResponse(PerfilResponse):
    access_token: str | None = None
    token_type: str | None = None


class AlterarSenhaPayload(BaseModel):
    senha_atual: str
    nova_senha: str

    @field_validator("nova_senha")
    @classmethod
    def validar_nova_senha(cls, v: str) -> str:
        return validar_forca_senha(v)


class ExcluirContaPayload(BaseModel):
    senha: str


class PessoaMonitoradaPayload(BaseModel):
    nome_completo: str


class PessoaMonitoradaResponse(BaseModel):
    id: int
    nome_completo: str | None = None


class PulseiraPayload(BaseModel):
    mac_address: str
    pessoa_monitorada_id: int
    versao_firmware: str | None = None


class PulseiraResponse(BaseModel):
    mac_address: str
    pessoa_monitorada_id: int | None = None
    pessoa_monitorada_nome: str | None = None
    versao_firmware: str | None = None
    status_ativo: bool


class TelemetriaEventoPayload(BaseModel):
    mac_address: str
    tipo_evento: str
    coordenadas_gps: str | None = None


class TelemetriaEventoResponse(BaseModel):
    id: int
    mac_address: str
    tipo_evento: str | None = None
    coordenadas_gps: str | None = None
    data_evento: datetime
    pessoa_monitorada_nome: str | None = None
