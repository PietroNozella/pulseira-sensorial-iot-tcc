"""
Configuração compartilhada dos testes.
Usa SQLite em memória para isolar os cenários de teste do banco real.
"""
import os
import pytest

# Define as variáveis mínimas esperadas pela aplicação antes de importar os
# módulos do projeto, garantindo que o ambiente de teste suba corretamente.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ.setdefault("JWT_SECRET", "chave-secreta-de-teste-fallsense")
os.environ.setdefault("MAIL_USERNAME", "teste@fallsense.com")
os.environ.setdefault("MAIL_PASSWORD", "senha-teste")
os.environ.setdefault("MAIL_FROM", "teste@fallsense.com")
os.environ.setdefault("MAIL_PORT", "587")
os.environ.setdefault("MAIL_SERVER", "smtp.gmail.com")

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Cria um banco SQLite em memória compartilhado pela suíte de testes. O uso de
# uma única conexão garante que o TestClient e os helpers enxerguem o mesmo
# estado de dados durante cada execução.
engine_teste = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    # Mantém a mesma conexão em memória ativa entre diferentes acessos.
    poolclass=__import__("sqlalchemy.pool", fromlist=["StaticPool"]).StaticPool,
)
SessionTeste = sessionmaker(autocommit=False, autoflush=False, bind=engine_teste)

# Redireciona o módulo principal de banco para usar a infraestrutura de teste
# antes de carregar a aplicação FastAPI.
import security.database as db_module
db_module.engine = engine_teste
db_module.SessionLocal = SessionTeste

from security.database import Base, get_db
from main import app


def sobrescrever_get_db():
    """Entrega uma sessão do banco de teste no lugar da conexão real."""
    db = SessionTeste()
    try:
        yield db
    finally:
        db.close()


# Aplica o override global para que todas as rotas testadas usem o banco em memória.
app.dependency_overrides[get_db] = sobrescrever_get_db


@pytest.fixture(autouse=True)
def banco_limpo():
    """Recria o schema a cada teste para evitar vazamento de estado entre casos."""
    Base.metadata.create_all(bind=engine_teste)
    yield
    Base.metadata.drop_all(bind=engine_teste)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def usuario_registrado(client):
    """Cria um usuário padrão para cenários que dependem de autenticação."""
    resposta = client.post("/auth/registrar", json={
        "nome_completo": "Pietro Teste",
        "email": "pietro@fallsense.com",
        "telefone": "11999999999",
        "senha": "Senha123"
    })
    assert resposta.status_code == 201
    return resposta.json()


def get_db_direto() -> SessionTeste:
    """Retorna uma sessão direta para helpers que acessam o banco fora das rotas."""
    return SessionTeste()
