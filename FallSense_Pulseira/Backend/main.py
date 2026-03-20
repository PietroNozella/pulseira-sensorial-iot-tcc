from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from security.database import engine, get_db, Base
from routers import auth, recuperacao

# Inicializa a aplicação FastAPI
app = FastAPI(title="FallSense API Segura")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # No TCC permite todo mundo (celular, web, etc)
    allow_credentials=True,
    allow_methods=["*"],  # Permite POST, GET, PUT, etc
    allow_headers=["*"],  # Permite mandar o Token JWT e senhas
)

# Cria as tabelas no Supabase automaticamente se elas não existirem!
Base.metadata.create_all(bind=engine)

# Adiciona as rotas de autenticação no sistema
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(recuperacao.router, prefix="/auth", tags=["Recuperação de Senha"])

# Rodas de teste do banco
@app.get("/teste-banco", tags=["Teste"])
def testar_banco(db: Session = Depends(get_db)):
    # Rota temporária para testar se a API consegue falar com o Supabase
    try:
        db.execute(text("SELECT 1"))
        return {"status": "SUCESSO!", "mensagem": "SQLAlchemy está conectado e rodando liso no Supabase!"}
    except Exception as e:
        return {"status": "ERRO", "detalhe": str(e)}