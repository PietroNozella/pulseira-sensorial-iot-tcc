import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Importa a conexão com o banco e o modelo
from security.database import get_db
from models.user import User

# Importa as ferramentas de segurança
from security.hashing import gerar_hash, verificar_senha
from security.jwt_handler import criar_token_jwt
from security.totp_handler import gerar_segredo_totp, verificar_totp
from schemas.auth_schemas import RegistroPayload, LoginPayload

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

    # Cria o novo usuário com senha criptografada e um 2FA único
    novo_usuario = User(
        email=payload.email,
        hashed_password=gerar_hash(payload.senha),
        totp_secret=gerar_segredo_totp()
    )
    
    # Salva no banco de dados usando o SQLAlchemy
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    return {
        "mensagem": "Usuário {} cadastrado com sucesso!".format(payload.nome_completo),
        "totp_secret": novo_usuario.totp_secret
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
        "token_type": "bearer",
        "requer_2fa": False
    }