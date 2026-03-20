import secrets
import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Importa a conexão com o banco e os modelos
from security.database import get_db
from models.user import User, TokenRecuperacao, LogAuditoria
from security.hashing import gerar_hash

# --- IMPORTAÇÃO DOS SCHEMAS ---
from schemas.auth_schemas import EsqueciSenhaPayload, ResetarSenhaPayload

router = APIRouter()

# Configuração do Logger de Auditoria
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Auditoria")

# --- FUNÇÃO AUXILIAR PARA SALVAR LOG NO BANCO ---
def registrar_log_banco(db: Session, usuario_id, acao: str, descricao: str, status: str):
    novo_log = LogAuditoria(
        usuario_id=usuario_id,
        acao=acao,
        descricao=descricao,
        data_hora=datetime.utcnow(),
        status=status
    )
    db.add(novo_log)
    db.commit()

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
    
    db.commit()

    # --- SIMULAÇÃO DE E-MAIL ---
    print(f"\n" + "="*10)
    print(f"E-MAIL ENVIADO PARA: {usuario.email}")
    print(f"SEU TOKEN DE RECUPERAÇÃO: {token_gerado}")
    print("="*10 + "\n")

    logger.info(f"[AUDITORIA] Log de Solicitação: E-mail de recuperação enviado com sucesso para o usuário ID {usuario.id}.")
    registrar_log_banco(db, usuario.id, "SOLICITACAO_RECUPERACAO", "E-mail de recuperação gerado", "SUCESSO")

    return {"mensagem": "Se o e-mail estiver cadastrado, as instruções serão enviadas."}

@router.post("/resetar-senha")
def resetar_senha(payload: ResetarSenhaPayload, db: Session = Depends(get_db)):
    # Busca o token na tabela token_recuperacao
    token_db = db.query(TokenRecuperacao).filter(
        TokenRecuperacao.token_hash == payload.token
    ).first()

    # Verifica se o token não existir
    if not token_db:
        logger.warning("[AUDITORIA] Log de Conclusão (Falha): Tentativa de redefinição com token inválido ou inexistente.")
        registrar_log_banco(db, None, "REDEFINICAO_SENHA", "Tentativa com token inexistente", "FALHA")
        raise HTTPException(status_code=400, detail="Token inválido ou inexistente.")

    # Caso já foi utilizado (Invalidação)
    if token_db.utilizado:
        logger.warning(f"[AUDITORIA] Log de Conclusão (Falha): Tentativa de redefinição com token já utilizado (Token fornecido: {payload.token}).")
        registrar_log_banco(db, token_db.usuario_id, "REDEFINICAO_SENHA", "Tentativa de reuso de token", "FALHA")
        raise HTTPException(status_code=400, detail="Este token já foi utilizado.")

    # Verifica se já foi expirado
    if token_db.data_expiracao < datetime.utcnow():
        logger.warning(f"[AUDITORIA] Log de Conclusão (Falha): Tentativa de redefinição com token expirado (Token fornecido: {payload.token}).")
        registrar_log_banco(db, token_db.usuario_id, "REDEFINICAO_SENHA", "Tentativa com token expirado", "FALHA")
        raise HTTPException(status_code=400, detail="O token expirou. Solicite um novo.")

    # Encontra o usuário dono do token na tabela usuarios_api
    usuario = db.query(User).filter(User.id == token_db.usuario_id).first()
    if not usuario:
        logger.error("[AUDITORIA] Log de Conclusão (Falha): Usuário não encontrado para um token válido no banco de dados.")
        registrar_log_banco(db, token_db.usuario_id, "REDEFINICAO_SENHA", "Usuário não encontrado para token válido", "FALHA")
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    # Substituição segura da senha
    usuario.hashed_password = gerar_hash(payload.nova_senha)

    # Token invalidado após uso nós marcamos como utilizado para manter histórico para auditoria
    token_db.utilizado = True
    db.commit()

    logger.info(f"[AUDITORIA] Log de Conclusão (Sucesso): Senha redefinida com sucesso para o usuário ID {usuario.id}.")
    registrar_log_banco(db, usuario.id, "REDEFINICAO_SENHA", "Senha alterada com sucesso", "SUCESSO")

    return {"mensagem": "Senha redefinida com sucesso!"}