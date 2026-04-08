from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from security.database import engine, get_db, Base
from models.user import LogAuditoria, TokenRevogado  # noqa: F401 — garante criação das tabelas
from routers import auth, recuperacao

# Inicializa a aplicação principal da API.
app = FastAPI(title="FallSense API Segura")
app.add_middleware(HTTPSRedirectMiddleware)

# Libera o acesso da aplicação por diferentes clientes durante o projeto,
# incluindo frontend web e aplicativo móvel.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite chamadas vindas de qualquer origem.
    allow_credentials=True,
    allow_methods=["*"],  # Aceita todos os métodos HTTP usados pela API.
    allow_headers=["*"],  # Aceita cabeçalhos como Authorization e Content-Type.
)

# Pode ser usado para criar as tabelas automaticamente a partir dos modelos ORM.
#Base.metadata.create_all(bind=engine)

# Registra os conjuntos de rotas de autenticação e recuperação de senha.
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(recuperacao.router, prefix="/auth", tags=["Recuperação de Senha"])

# Endpoint auxiliar para verificar rapidamente se a API consegue executar uma
# consulta simples no banco configurado.
@app.get("/teste-banco", tags=["Teste"])
def testar_banco(db: Session = Depends(get_db)):
    # O SELECT 1 é uma consulta mínima usada só para validar conectividade.
    try:
        db.execute(text("SELECT 1"))
        return {"status": "SUCESSO!", "mensagem": "SQLAlchemy está conectado e rodando liso no Supabase!"}
    except Exception as e:
        return {"status": "ERRO", "detalhe": str(e)}

# Endpoint auxiliar para inspecionar os registros mais recentes de auditoria.
@app.get("/logs-auditoria", tags=["Teste"])
def ver_logs(db: Session = Depends(get_db)):
    logs = db.query(LogAuditoria).order_by(LogAuditoria.data_hora.desc()).limit(10).all()
    return {"logs_recentes": logs}
