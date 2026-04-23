from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.user import PessoaMonitorada, Pulseira
from routers.pessoa_monitorada import _obter_usuario_autenticado
from schemas.auth_schemas import PulseiraPayload, PulseiraResponse
from security.database import get_db

router = APIRouter()


@router.get("", response_model=list[PulseiraResponse])
def listar_pulseiras(
    authorization: str = Header(..., description="Bearer <token>"),
    db: Session = Depends(get_db),
):
    usuario = _obter_usuario_autenticado(authorization, db)
    pessoas_ids = select(PessoaMonitorada.id).filter(
        PessoaMonitorada.usuario_responsavel_id == usuario.id
    )

    pulseiras = (
        db.query(Pulseira, PessoaMonitorada.nome_completo)
        .outerjoin(PessoaMonitorada, PessoaMonitorada.id == Pulseira.pessoa_monitorada_id)
        .filter(Pulseira.pessoa_monitorada_id.in_(pessoas_ids))
        .order_by(Pulseira.registrado_em.asc(), Pulseira.mac_address.asc())
        .all()
    )

    return [
        PulseiraResponse(
            mac_address=pulseira.mac_address,
            pessoa_monitorada_id=pulseira.pessoa_monitorada_id,
            pessoa_monitorada_nome=nome,
            versao_firmware=pulseira.versao_firmware,
            status_ativo=bool(pulseira.status_ativo),
        )
        for pulseira, nome in pulseiras
    ]


@router.post("", response_model=PulseiraResponse, status_code=201)
def cadastrar_pulseira(
    payload: PulseiraPayload,
    authorization: str = Header(..., description="Bearer <token>"),
    db: Session = Depends(get_db),
):
    usuario = _obter_usuario_autenticado(authorization, db)
    pessoa = (
        db.query(PessoaMonitorada)
        .filter(
            PessoaMonitorada.id == payload.pessoa_monitorada_id,
            PessoaMonitorada.usuario_responsavel_id == usuario.id,
        )
        .first()
    )

    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa monitorada não encontrada.")

    mac_address = payload.mac_address.strip()
    if not mac_address:
        raise HTTPException(status_code=400, detail="MAC address inválido.")

    existente = db.query(Pulseira).filter(Pulseira.mac_address == mac_address).first()
    if existente:
        raise HTTPException(status_code=400, detail="Pulseira já cadastrada.")

    nova_pulseira = Pulseira(
        mac_address=mac_address,
        pessoa_monitorada_id=pessoa.id,
        versao_firmware=payload.versao_firmware.strip() if payload.versao_firmware else None,
        status_ativo=True,
    )
    db.add(nova_pulseira)
    db.commit()
    db.refresh(nova_pulseira)

    return PulseiraResponse(
        mac_address=nova_pulseira.mac_address,
        pessoa_monitorada_id=nova_pulseira.pessoa_monitorada_id,
        pessoa_monitorada_nome=pessoa.nome_completo,
        versao_firmware=nova_pulseira.versao_firmware,
        status_ativo=bool(nova_pulseira.status_ativo),
    )
