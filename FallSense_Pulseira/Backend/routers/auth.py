import time
import json
import secrets
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

# Importa a conexão com o banco e o modelo
from security.database import get_db
from models.user import User, LogAuditoria

# Importa as ferramentas de segurança
from security.hashing import gerar_hash, verificar_senha
from security.jwt_handler import criar_token_jwt, verificar_token_jwt, revogar_token
from security.totp_handler import gerar_segredo_totp, verificar_totp
from schemas.auth_schemas import PerfilResponse, RegistroPayload, LoginPayload


def _gerar_recovery_codes() -> tuple[list[str], str]:
    """Gera 8 códigos de recuperação legíveis e retorna os códigos em texto
    e o JSON com seus hashes para armazenar no banco."""
    codigos = [secrets.token_hex(4).upper() for _ in range(8)]  # ex: "A3F2B1C9"
    hashes = json.dumps([gerar_hash(c) for c in codigos])
    return codigos, hashes

router = APIRouter()

# Config de brute force
MAX_FAILED_ATTEMPTS = 3
LOCKOUT_TIME_SECONDS = 300 # 5 minutos de bloqueio

@router.post("/registrar", status_code=201)
def registrar_usuario(payload: RegistroPayload, db: Session = Depends(get_db)):
    # Verifica se o e-mail já existe no banco
    usuario_existente = db.query(User).filter(User.email == payload.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado no sistema.")

    # Gera os recovery codes antes de criar o usuário
    codigos_texto, codigos_hash = _gerar_recovery_codes()

    # Cria o novo usuário com senha criptografada, 2FA único e recovery codes
    novo_usuario = User(
        nome_completo=payload.nome_completo,
        email=payload.email,
        telefone=payload.telefone,
        hashed_password=gerar_hash(payload.senha),
        totp_secret=gerar_segredo_totp(),
        recovery_codes_hash=codigos_hash
    )

    # Salva no banco de dados usando o SQLAlchemy
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return {
        "mensagem": "Usuário {} cadastrado com sucesso!".format(payload.nome_completo),
        "totp_secret": novo_usuario.totp_secret,
        # Enviados apenas uma vez — o usuário deve guardar esses códigos
        "recovery_codes": codigos_texto
    }


@router.post("/login")
def login_usuario(payload: LoginPayload, db: Session = Depends(get_db)):
    # Busca o usuário pelo e-mail
    usuario = db.query(User).filter(User.email == payload.email).first()

    if not usuario:
        raise HTTPException(status_code=400, detail="Credenciais inválidas.")

    # Verifica se a conta está bloqueada
    tempo_atual = time.time()
    if usuario.lockout_until > tempo_atual:
        tempo_restante = int(usuario.lockout_until - tempo_atual)
        raise HTTPException(
            status_code=429, 
            detail="Conta temporariamente bloqueada. Tente novamente em {} segundos.".format(tempo_restante)
        )

    # VALIDAÇÃO DE SENHA
    if not verificar_senha(usuario.hashed_password, payload.senha):
        # Adiciona 1 falha na conta
        usuario.failed_attempts += 1
        if usuario.failed_attempts >= MAX_FAILED_ATTEMPTS:
            # Tranca a porta por 5 minutos caso erre 3 vezes
            usuario.lockout_until = time.time() + LOCKOUT_TIME_SECONDS
        db.commit()
        raise HTTPException(status_code=400, detail="Credenciais inválidas.")

    # VALIDAÇÃO DE 2FA (Google Authenticator)
    if not payload.codigo_2fa:
        return {"requer_2fa": True, "mensagem": "Senha correta. Insira o código 2FA."}

    # Se o Flutter enviou o código, vamos validar
    codigo_limpo = payload.codigo_2fa.replace(" ", "")
    
    if not verificar_totp(usuario.totp_secret, codigo_limpo):
        usuario.failed_attempts += 1
        if usuario.failed_attempts >= 3:
            usuario.lockout_until = time.time() + 300
        db.commit()
        raise HTTPException(status_code=400, detail="Código 2FA inválido.")

    # Reseta as falhas e o bloqueio para zero
    usuario.failed_attempts = 0
    usuario.lockout_until = 0.0
    db.commit()

    # Gera o Token JWT
    token_acesso = criar_token_jwt(usuario.email)

    return {
        "mensagem": "Autenticação realizada com sucesso!",
        "access_token": token_acesso,
        "nome_completo": usuario.nome_completo,
        "token_type": "bearer",
        "requer_2fa": False
    }


@router.post("/logout")
def logout_usuario(
    authorization: str = Header(..., description="Bearer <token>"),
    db: Session = Depends(get_db)
):
    # Extrai o token do header Authorization: Bearer <token>
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Formato de token inválido.")

    token = authorization.removeprefix("Bearer ").strip()

    # Valida o token (assinatura, expiração e blacklist) e recupera o e-mail
    email = verificar_token_jwt(token, db)

    # Insere o token na blacklist — impede qualquer reuso após logout
    revogar_token(token, db)

    # Registra a ação no log de auditoria para rastreabilidade
    usuario = db.query(User).filter(User.email == email).first()
    db.add(LogAuditoria(
        usuario_id=usuario.id if usuario else None,
        acao="LOGOUT",
        descricao="Sessão encerrada e token JWT revogado para o usuário {}.".format(email),
        status="SUCESSO"
    ))
    db.commit()

    return {"mensagem": "Logout realizado com sucesso. Token invalidado."}


@router.get("/me", response_model=PerfilResponse)
def obter_perfil_usuario(
    authorization: str = Header(..., description="Bearer <token>"),
    db: Session = Depends(get_db)
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Formato de token inválido.")

    token = authorization.removeprefix("Bearer ").strip()
    email = verificar_token_jwt(token, db)
    usuario = db.query(User).filter(User.email == email).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return PerfilResponse(
        nome_completo=usuario.nome_completo,
        email=usuario.email,
        telefone=usuario.telefone
    )
