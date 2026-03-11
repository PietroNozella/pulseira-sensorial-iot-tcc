import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv, find_dotenv

# 1. Carrega o nosso cofre invisível
load_dotenv(find_dotenv())

DB_URL = os.getenv("DATABASE_URL")

# Trava de segurança
if not DB_URL:
    raise ValueError("⚠️ ALERTA: A variável DATABASE_URL não foi encontrada no arquivo .env!")

# 2. Cria o "Motor" do SQLAlchemy conectado ao Supabase
engine = create_engine(DB_URL)

# 3. Cria a "Fábrica de Sessões" do banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Classe base que será usada para transformar as nossas classes Python em Tabelas reais
class Base(DeclarativeBase):
    pass

# 5. O "Entregador" de conexões (Injeção de Dependência para o FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # Garante que a conexão será fechada mesmo se der erro na rota