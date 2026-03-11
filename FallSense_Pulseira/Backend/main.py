# backend/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from security.database import engine, get_db, Base
from models import user
from routers import auth

# Inicializa a aplicação FastAPI
app = FastAPI(title="FallSense API Segura")

# Cria as tabelas no Supabase automaticamente se elas não existirem!
Base.metadata.create_all(bind=engine)

# Adiciona as rotas de autenticação no sistema
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])

# ROTA DE TESTE DO BANCO
@app.get("/teste-banco", tags=["Teste"])
def testar_banco(db: Session = Depends(get_db)):
    # Rota temporária para testar se a API consegue falar com o Supabase
    try:
        db.execute(text("SELECT 1"))
        return {"status": "SUCESSO!", "mensagem": "SQLAlchemy está conectado e rodando liso no Supabase!"}
    except Exception as e:
        return {"status": "ERRO", "detalhe": str(e)}