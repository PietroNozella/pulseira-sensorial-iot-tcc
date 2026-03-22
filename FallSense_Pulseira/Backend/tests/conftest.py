"""
Configuração compartilhada dos testes.
Usa SQLite em memória para não depender do Supabase durante os testes.
"""
import os
import pytest

# Define variáveis de ambiente obrigatórias antes de qualquer import do projeto
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

# Engine SQLite em memória com uma única conexão compartilhada entre todos os acessos
# (necessário para que o TestClient e os helpers de teste vejam os mesmos dados)
engine_teste = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    # Força todas as requisições a reutilizarem a mesma conexão em memória
    poolclass=__import__("sqlalchemy.pool", fromlist=["StaticPool"]).StaticPool,
)
SessionTeste = sessionmaker(autocommit=False, autoflush=False, bind=engine_teste)

# Substitui o engine do módulo database antes de importar o app
import security.database as db_module
db_module.engine = engine_teste
db_module.SessionLocal = SessionTeste

from security.database import Base, get_db
from main import app


def sobrescrever_get_db():
    """Substitui a conexão real (Supabase) pelo banco de teste (SQLite)."""
    db = SessionTeste()
    try:
        yield db
    finally:
        db.close()


# Substitui a dependência de banco em toda a aplicação durante os testes
app.dependency_overrides[get_db] = sobrescrever_get_db


@pytest.fixture(autouse=True)
def banco_limpo():
    """Recria todas as tabelas antes de cada teste e limpa ao fim."""
    Base.metadata.create_all(bind=engine_teste)
    yield
    Base.metadata.drop_all(bind=engine_teste)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def usuario_registrado(client):
    """Registra um usuário e retorna os dados incluindo totp_secret."""
    resposta = client.post("/auth/registrar", json={
        "nome_completo": "Pietro Teste",
        "email": "pietro@fallsense.com",
        "telefone": "11999999999",
        "senha": "Senha123"
    })
    assert resposta.status_code == 201
    return resposta.json()


def get_db_direto() -> SessionTeste:
    """Retorna uma sessão direta (sem yield) para uso nos helpers dos testes."""
    return SessionTeste()
