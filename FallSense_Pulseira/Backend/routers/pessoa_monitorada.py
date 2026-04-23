from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from models.user import PessoaMonitorada, User
from schemas.auth_schemas import PessoaMonitoradaPayload, PessoaMonitoradaResponse
from security.database import get_db
from security.jwt_handler import verificar_token_jwt

router = APIRouter()


def _obter_usuario_autenticado(authorization: str, db: Session) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Formato de token inválido.")

    token = authorization.removeprefix("Bearer ").strip()
    email = verificar_token_jwt(token, db)
    usuario = db.query(User).filter(User.email == email).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return usuario


@router.get("", response_model=list[PessoaMonitoradaResponse])
def listar_pessoas_monitoradas(
    authorization: str = Header(..., description="Bearer <token>"),
    db: Session = Depends(get_db),
):
    usuario = _obter_usuario_autenticado(authorization, db)
    pessoas = (
        db.query(PessoaMonitorada)
        .filter(PessoaMonitorada.usuario_responsavel_id == usuario.id)
        .order_by(PessoaMonitorada.id.asc())
        .all()
    )

    return [
        PessoaMonitoradaResponse(
            id=pessoa.id,
            nome_completo=pessoa.nome_completo,
        )
        for pessoa in pessoas
    ]


@router.post("", response_model=PessoaMonitoradaResponse, status_code=201)
def cadastrar_pessoa_monitorada(
    payload: PessoaMonitoradaPayload,
    authorization: str = Header(..., description="Bearer <token>"),
    db: Session = Depends(get_db),
):
    usuario = _obter_usuario_autenticado(authorization, db)

    nova_pessoa = PessoaMonitorada(
        usuario_responsavel_id=usuario.id,
        nome_completo=payload.nome_completo.strip(),
    )
    db.add(nova_pessoa)
    db.commit()
    db.refresh(nova_pessoa)

    return PessoaMonitoradaResponse(
        id=nova_pessoa.id,
        nome_completo=nova_pessoa.nome_completo,
    )
