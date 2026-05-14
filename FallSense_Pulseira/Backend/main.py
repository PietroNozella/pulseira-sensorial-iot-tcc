from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from models.user import LogAuditoria, TokenRevogado  # noqa: F401
# Importamos o novo roteador de compliance (conformidade)
from routers import auth, compliance, pessoa_monitorada, pulseira, recuperacao, telemetria
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

# Rota para gestão de Termos de Uso e Compliance LGPD
app.include_router(compliance.router, prefix="/compliance", tags=["Conformidade e LGPD"])


@app.get("/health", tags=["Health"])
#Retorna rapidamente se o processo da API está ativo
def verificar_saude():
    return {"status": "ok"}


@app.get("/teste-banco", tags=["Teste"])
# Valida conectividade básica com o banco configurado
def testar_banco(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "SUCESSO!",
            "mensagem": "SQLAlchemy está conectado e rodando liso no Supabase!",
        }
    except Exception as exc:
        return {"status": "ERRO", "detalhe": str(exc)}


@app.get("/logs-auditoria", tags=["Teste"])
#Retorna os registros mais recentes do log de auditoria persistidos no banco
def ver_logs(db: Session = Depends(get_db)):
    logs = db.query(LogAuditoria).order_by(LogAuditoria.data_hora.desc()).limit(10).all()
    return {"logs_recentes": logs}