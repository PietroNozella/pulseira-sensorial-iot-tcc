import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Importa a conexão com o banco e os modelos
from security.database import get_db
from models.user import User, TokenRecuperacao
from security.hashing import gerar_hash

# --- IMPORTAÇÃO DOS SCHEMAS ---
from schemas.auth_schemas import EsqueciSenhaPayload, ResetarSenhaPayload

router = APIRouter()

@router.post("/esqueci-senha")
def solicitar_recuperacao(payload: EsqueciSenhaPayload, db: Session = Depends(get_db)):
    # Busca se o usuário existe no banco
    usuario = db.query(User).filter(User.email == payload.email).first()

    # Nunca avisar se o e-mail não existe.
    if not usuario:
        return {"mensagem": "Se o e-mail estiver cadastrado, as instruções serão enviadas."}

    # Gera um token criptograficamente seguro de 32 bytes (aleatório e único)
    token_gerado = secrets.token_urlsafe(32)
    expiracao = datetime.utcnow() + timedelta(minutes=15)

    # Salva na nossa tabela de tokens do Supabase
    novo_token = TokenRecuperacao(
        usuario_id=usuario.id,
        token_hash=token_gerado,
        utilizado=False,
        data_expiracao=expiracao
    )
    
    db.add(novo_token)
    
    # Registro simples de auditoria no console
    print(f"[AUDITORIA - LOG] Solicitação de recuperação gerada para o ID {usuario.id} em {datetime.utcnow()}")
    db.commit()

    # --- SIMULAÇÃO DE E-MAIL ---
    print(f"\n" + "="*10)
    print(f"E-MAIL ENVIADO PARA: {usuario.email}")
    print(f"SEU TOKEN DE RECUPERAÇÃO: {token_gerado}")
    print("="*10 + "\n")

    return {"mensagem": "Se o e-mail estiver cadastrado, as instruções serão enviadas."}

@router.post("/resetar-senha")
def resetar_senha(payload: ResetarSenhaPayload, db: Session = Depends(get_db)):
    # Busca o token na tabela token_recuperacao
    token_db = db.query(TokenRecuperacao).filter(
        TokenRecuperacao.token_hash == payload.token
    ).first()

    # Verifica se o token não existir
    if not token_db:
        raise HTTPException(status_code=400, detail="Token inválido ou inexistente.")

    # Caso já foi utilizado (Invalidação)
    if token_db.utilizado:
        raise HTTPException(status_code=400, detail="Este token já foi utilizado.")

    # Verifica se já foi expirado
    if token_db.data_expiracao < datetime.utcnow():
        raise HTTPException(status_code=400, detail="O token expirou. Solicite um novo.")

    # Encontra o usuário dono do token na tabela usuarios_api
    usuario = db.query(User).filter(User.id == token_db.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    # Substituição segura da senha
    usuario.hashed_password = gerar_hash(payload.nova_senha)

    # Token invalidado após uso nós marcamos como utilizado para manter histórico para auditoria
    token_db.utilizado = True
    db.commit()

    return {"mensagem": "Senha redefinida com sucesso!"}