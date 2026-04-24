import json
import secrets
import time

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from models.user import LogAuditoria, User
from schemas.auth_schemas import LoginPayload, PerfilResponse, RegistroPayload
from security.database import get_db
from security.hashing import gerar_hash, verificar_senha
from security.jwt_handler import criar_token_jwt, revogar_token, verificar_token_jwt
from security.totp_handler import gerar_segredo_totp, gerar_uri_totp, verificar_totp

router = APIRouter()

MAX_FAILED_ATTEMPTS = 3
LOCKOUT_TIME_SECONDS = 300
LOGIN_CHALLENGE_TTL_SECONDS = 120

login_challenges: dict[str, dict[str, float | str]] = {}


def _gerar_recovery_codes() -> tuple[list[str], str]:
    codigos = [secrets.token_hex(4).upper() for _ in range(8)]
    hashes = json.dumps([gerar_hash(codigo) for codigo in codigos])
    return codigos, hashes


def _limpar_challenges_expirados() -> None:
    agora = time.time()
    expirados = [
        challenge_id
        for challenge_id, challenge in login_challenges.items()
        if float(challenge["expires_at"]) <= agora
    ]

    for challenge_id in expirados:
        login_challenges.pop(challenge_id, None)


def _criar_login_challenge(email: str) -> str:
    _limpar_challenges_expirados()

    challenge_id = secrets.token_urlsafe(32)
    login_challenges[challenge_id] = {
        "email": email,
        "expires_at": time.time() + LOGIN_CHALLENGE_TTL_SECONDS,
    }

    return challenge_id


def _challenge_valido(email: str, challenge_id: str) -> bool:
    _limpar_challenges_expirados()

    challenge = login_challenges.get(challenge_id)
    if not challenge:
        return False

    return challenge["email"] == email and float(challenge["expires_at"]) > time.time()


def _remover_login_challenge(challenge_id: str | None) -> None:
    if challenge_id:
        login_challenges.pop(challenge_id, None)


def _emitir_token_login(
    usuario: User,
    db: Session,
    challenge_id: str | None = None,
):
    usuario.failed_attempts = 0
    usuario.lockout_until = 0.0
    db.commit()
    _remover_login_challenge(challenge_id)

    token_acesso = criar_token_jwt(usuario.email)

    return {
        "mensagem": "Autenticação realizada com sucesso!",
        "access_token": token_acesso,
        "nome_completo": usuario.nome_completo,
        "token_type": "bearer",
        "requer_2fa": False,
    }


def _registrar_falha_login(usuario: User, db: Session, challenge_id: str | None = None):
    usuario.failed_attempts += 1
    if usuario.failed_attempts >= MAX_FAILED_ATTEMPTS:
        usuario.lockout_until = time.time() + LOCKOUT_TIME_SECONDS
        _remover_login_challenge(challenge_id)
    db.commit()


@router.post("/registrar", status_code=201)
def registrar_usuario(payload: RegistroPayload, db: Session = Depends(get_db)):
    usuario_existente = db.query(User).filter(User.email == payload.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado no sistema.")

    codigos_texto, codigos_hash = _gerar_recovery_codes()

    novo_usuario = User(
        nome_completo=payload.nome_completo,
        email=payload.email,
        telefone=payload.telefone,
        hashed_password=gerar_hash(payload.senha),
        totp_secret=gerar_segredo_totp(),
        recovery_codes_hash=codigos_hash,
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return {
        "mensagem": "Usuário {} cadastrado com sucesso!".format(
            payload.nome_completo
        ),
        "totp_secret": novo_usuario.totp_secret,
        "totp_uri": gerar_uri_totp(novo_usuario.totp_secret, novo_usuario.email),
        "recovery_codes": codigos_texto,
    }


@router.post("/login")
def login_usuario(payload: LoginPayload, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.email == payload.email).first()
    if not usuario:
        raise HTTPException(status_code=400, detail="Credenciais inválidas.")

    tempo_atual = time.time()
    if usuario.lockout_until > tempo_atual:
        tempo_restante = int(usuario.lockout_until - tempo_atual)
        raise HTTPException(
            status_code=429,
            detail="Conta temporariamente bloqueada. Tente novamente em {} segundos.".format(
                tempo_restante
            ),
        )

    if payload.challenge_id and payload.codigo_2fa:
        if not _challenge_valido(usuario.email, payload.challenge_id):
            raise HTTPException(
                status_code=400,
                detail="Sessão 2FA expirada. Informe e-mail e senha novamente.",
            )

        codigo_limpo = payload.codigo_2fa.replace(" ", "")
        if not verificar_totp(usuario.totp_secret, codigo_limpo):
            _registrar_falha_login(usuario, db, payload.challenge_id)
            raise HTTPException(status_code=400, detail="Código 2FA inválido.")

        return _emitir_token_login(usuario, db, payload.challenge_id)

    if not payload.senha:
        raise HTTPException(status_code=400, detail="Credenciais inválidas.")

    if not verificar_senha(usuario.hashed_password, payload.senha):
        _registrar_falha_login(usuario, db)
        raise HTTPException(status_code=400, detail="Credenciais inválidas.")

    if not payload.codigo_2fa:
        challenge_id = _criar_login_challenge(usuario.email)
        return {
            "requer_2fa": True,
            "mensagem": "Senha correta. Insira o código 2FA.",
            "challenge_id": challenge_id,
            "expires_in": LOGIN_CHALLENGE_TTL_SECONDS,
        }

    codigo_limpo = payload.codigo_2fa.replace(" ", "")
    if not verificar_totp(usuario.totp_secret, codigo_limpo):
        _registrar_falha_login(usuario, db)
        raise HTTPException(status_code=400, detail="Código 2FA inválido.")

    return _emitir_token_login(usuario, db)


@router.post("/logout")
def logout_usuario(
    authorization: str = Header(..., description="Bearer <token>"),
    db: Session = Depends(get_db),
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Formato de token inválido.")

    token = authorization.removeprefix("Bearer ").strip()
    email = verificar_token_jwt(token, db)
    revogar_token(token, db)

    usuario = db.query(User).filter(User.email == email).first()
    db.add(
        LogAuditoria(
            usuario_id=usuario.id if usuario else None,
            acao="LOGOUT",
            descricao="Sessão encerrada e token JWT revogado para o usuário {}.".format(
                email
            ),
            status="SUCESSO",
        )
    )
    db.commit()

    return {"mensagem": "Logout realizado com sucesso. Token invalidado."}


@router.get("/me", response_model=PerfilResponse)
def obter_perfil_usuario(
    authorization: str = Header(..., description="Bearer <token>"),
    db: Session = Depends(get_db),
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
        telefone=usuario.telefone,
    )
