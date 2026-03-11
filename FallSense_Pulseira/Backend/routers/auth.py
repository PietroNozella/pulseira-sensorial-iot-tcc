# backend/routers/auth.py
import time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

# 1. Importa a conexão com o banco (SQLAlchemy)
from security.database import get_db

# 2. Importa o modelo da Tabela (A "Planta Baixa" que criamos)
from models.user import User

# 3. Importa as nossas ferramentas de segurança blindadas
from security.hashing import gerar_hash, verificar_senha
from security.jwt_handler import criar_token_jwt
from security.totp_handler import gerar_segredo_totp, verificar_totp

router = APIRouter()

# --- CONFIGURAÇÕES DE BRUTE FORCE (Frente 3) ---
MAX_FAILED_ATTEMPTS = 3
LOCKOUT_TIME_SECONDS = 300 # 5 minutos de bloqueio

# --- MODELOS PYDANTIC (Validação do JSON do Swagger) ---
class RegistroPayload(BaseModel):
    nome_completo: str
    email: EmailStr
    telefone: str
    senha: str

class LoginPayload(BaseModel):
    email: EmailStr
    senha: str
    codigo_2fa: str | None = None  # Opcional na requisição para não quebrar testes antigos

# --- ROTAS ---

@router.post("/registrar", status_code=201)
def registrar_usuario(payload: RegistroPayload, db: Session = Depends(get_db)):
    # 1. Verifica se o e-mail já existe no banco
    usuario_existente = db.query(User).filter(User.email == payload.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado no sistema.")

    # 2. Cria o novo usuário com senha criptografada e um segredo 2FA único
    novo_usuario = User(
        email=payload.email,
        hashed_password=gerar_hash(payload.senha),
        totp_secret=gerar_segredo_totp(),
        is_2fa_enabled=True
    )
    
    # 3. Salva no banco de dados usando o SQLAlchemy
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    return {"mensagem": f"Usuário {payload.nome_completo} cadastrado com sucesso!"}


@router.post("/login")
def login_usuario(payload: LoginPayload, db: Session = Depends(get_db)):
    # 1. Busca o usuário pelo e-mail
    usuario = db.query(User).filter(User.email == payload.email).first()

    if not usuario:
        raise HTTPException(status_code=400, detail="Credenciais inválidas.")

    # 2. Verifica se a conta está bloqueada
    tempo_atual = time.time()
    if usuario.lockout_until > tempo_atual:
        tempo_restante = int(usuario.lockout_until - tempo_atual)
        raise HTTPException(
            status_code=429, 
            detail=f"Conta temporariamente bloqueada. Tente novamente em {tempo_restante} segundos."
        )

    # 3. VALIDAÇÃO DE SENHA
    if not verificar_senha(usuario.hashed_password, payload.senha):
        # Adiciona 1 falha na conta
        usuario.failed_attempts += 1
        if usuario.failed_attempts >= MAX_FAILED_ATTEMPTS:
            # Tranca a porta por 5 minutos caso erre 3 vezes
            usuario.lockout_until = time.time() + LOCKOUT_TIME_SECONDS
        db.commit()
        raise HTTPException(status_code=400, detail="Credenciais inválidas.")

    # 4. VALIDAÇÃO DE 2FA (Google Authenticator)
    if usuario.is_2fa_enabled:
        if not payload.codigo_2fa:
            raise HTTPException(status_code=400, detail="Código 2FA obrigatório para este usuário.")
        if usuario.totp_secret is None:
            raise HTTPException(status_code=400, detail="2FA não configurado para este usuário.")
        if not verificar_totp(usuario.totp_secret, payload.codigo_2fa):
            # Errou o código 2FA — conta como falha também
            usuario.failed_attempts += 1
            if usuario.failed_attempts >= MAX_FAILED_ATTEMPTS:
                usuario.lockout_until = time.time() + LOCKOUT_TIME_SECONDS
            db.commit()
            raise HTTPException(status_code=400, detail="Código 2FA inválido.")
        usuario.last_2fa_at = datetime.utcnow()

    # 5. Reseta as falhas e o bloqueio para zero
    usuario.failed_attempts = 0
    usuario.lockout_until = 0.0
    db.commit()

    # 6. Gera o Token JWT
    token_acesso = criar_token_jwt(usuario.email)

    return {
        "mensagem": "Autenticação realizada com sucesso!", 
        "access_token": token_acesso, 
        "token_type": "bearer",
        "2fa_requirido": True
    }