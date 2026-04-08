import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv, find_dotenv

# Carrega as variáveis de ambiente para disponibilizar a configuração de acesso
# ao banco de dados.
load_dotenv(find_dotenv())

DB_URL = os.getenv("DATABASE_URL")

# Sem a URL de conexão, a aplicação não consegue abrir sessões com o banco; por
# isso a inicialização é interrompida imediatamente.
if not DB_URL:
    raise ValueError("⚠️ ALERTA: A variável DATABASE_URL não foi encontrada no arquivo .env!")

# Cria o engine do SQLAlchemy, responsável por manter a comunicação com o banco.
engine = create_engine(DB_URL)

# Define uma fábrica de sessões. Cada sessão criada a partir daqui será usada
# pelas rotas e serviços para executar operações no banco.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base que será herdada pelos modelos ORM mapeados em tabelas.
class Base(DeclarativeBase):
    pass

# Dependência usada pelo FastAPI para entregar uma sessão de banco por request.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        # Fecha a sessão mesmo quando ocorre erro, evitando vazamento de conexão.
        db.close()
