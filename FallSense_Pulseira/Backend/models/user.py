"""Modelos do banco de dados (PostgreSQL / SQLAlchemy)."""
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.sql import func
from security.database import Base


class User(Base):
    """
    Modelo de usuário para o SQLAlchemy.
    Define a estrutura da tabela 'usuarios_api' no Supabase.
    """
    __tablename__ = "usuarios_api"

    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    telefone = Column(String, nullable=True)
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


class LogAuditoria(Base):
    """Tabela de logs de auditoria para rastreabilidade de ações críticas."""
    __tablename__ = "logs_auditoria"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios_api.id", ondelete="SET NULL"), nullable=True)
    acao = Column(String, nullable=False)
    descricao = Column(String, nullable=False)
    data_hora = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, nullable=False)

class TokenRevogado(Base):
    """Blacklist de tokens JWT revogados via logout."""
    __tablename__ = "tokens_revogados"

    id = Column(Integer, primary_key=True, index=True)
    # O token JWT completo revogado
    token = Column(String, unique=True, index=True, nullable=False)
    # Momento em que o logout foi efetuado
    revogado_em = Column(DateTime(timezone=True), server_default=func.now())


class TokenRecuperacao(Base):
    """Tabela para armazenar os tokens temporários de esqueci a senha."""
    __tablename__ = "tokens_recuperacao"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    # Define quando o link de recuperação expira (ex: 1 hora)
    expiracao = Column(DateTime, nullable=False)
    usado = Column(Boolean, default=False)


class PessoaMonitorada(Base):
    """Primeira entidade de dominio vinculada ao usuario autenticado."""
    __tablename__ = "pessoa_monitorada"

    id = Column(Integer, primary_key=True, index=True)
    usuario_responsavel_id = Column(
        Integer,
        ForeignKey("usuarios_api.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nome_completo = Column(String, nullable=True)
    consentimento_lgpd_data = Column(DateTime, nullable=True)
