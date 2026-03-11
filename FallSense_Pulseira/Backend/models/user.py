"""Modelos do banco de dados (PostgreSQL / SQLAlchemy)."""
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from security.database import Base


class User(Base):
    """
    Modelo de usuário para o SQLAlchemy.
    Define a estrutura da tabela 'usuarios_api' no Supabase.
    """
    __tablename__ = "usuarios_api"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # 2FA
    totp_secret = Column(String, nullable=True)
    is_2fa_enabled = Column(Boolean, default=True, nullable=False)
    recovery_codes_hash = Column(String, nullable=True)  # JSON de hashes
    last_2fa_at = Column(DateTime, nullable=True)

    # Proteção contra força bruta
    failed_attempts = Column(Integer, default=0, nullable=False)
    lockout_until = Column(Float, default=0.0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
