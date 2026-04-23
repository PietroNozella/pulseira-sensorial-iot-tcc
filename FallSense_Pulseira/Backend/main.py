from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from models.user import LogAuditoria, TokenRevogado  # noqa: F401
from routers import auth, pessoa_monitorada, pulseira, recuperacao, telemetria
from security.database import Base, engine, get_db

# Inicializa a aplicação principal da API.
app = FastAPI(title="FallSense API Segura")
app.add_middleware(HTTPSRedirectMiddleware)

# Libera o acesso da aplicação por diferentes clientes durante o projeto,
# incluindo frontend web e aplicativo móvel.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pode ser usado para criar as tabelas automaticamente a partir dos modelos ORM.
# Base.metadata.create_all(bind=engine)
_ = (Base, engine)

# Registra os conjuntos de rotas principais da API.
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(recuperacao.router, prefix="/auth", tags=["Recuperação de Senha"])
app.include_router(pessoa_monitorada.router, prefix="/monitorados", tags=["Pessoa Monitorada"])
app.include_router(pulseira.router, prefix="/pulseiras", tags=["Pulseira"])
app.include_router(telemetria.router, prefix="/eventos", tags=["Telemetria"])


@app.get("/teste-banco", tags=["Teste"])
def testar_banco(db: Session = Depends(get_db)):
    """Valida conectividade básica com o banco configurado."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "SUCESSO!",
            "mensagem": "SQLAlchemy está conectado e rodando liso no Supabase!",
        }
    except Exception as exc:
        return {"status": "ERRO", "detalhe": str(exc)}


@app.get("/logs-auditoria", tags=["Teste"])
def ver_logs(db: Session = Depends(get_db)):
    """Retorna os registros mais recentes do log de auditoria."""
    logs = db.query(LogAuditoria).order_by(LogAuditoria.data_hora.desc()).limit(10).all()
    return {"logs_recentes": logs}
