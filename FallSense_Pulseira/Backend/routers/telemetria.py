from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.user import PessoaMonitorada, Pulseira, TelemetriaEvento
from routers.pessoa_monitorada import _obter_usuario_autenticado
from schemas.auth_schemas import TelemetriaEventoPayload, TelemetriaEventoResponse
from security.database import get_db

router = APIRouter()


@router.get("", response_model=list[TelemetriaEventoResponse])
def listar_eventos_telemetria(
    authorization: str = Header(..., description="Bearer <token>"),
    db: Session = Depends(get_db),
):
    usuario = _obter_usuario_autenticado(authorization, db)
    pessoas_ids = select(PessoaMonitorada.id).filter(
        PessoaMonitorada.usuario_responsavel_id == usuario.id
    )

    eventos = (
        db.query(TelemetriaEvento, PessoaMonitorada.nome_completo)
        .join(Pulseira, Pulseira.mac_address == TelemetriaEvento.mac_address)
        .outerjoin(PessoaMonitorada, PessoaMonitorada.id == Pulseira.pessoa_monitorada_id)
        .filter(Pulseira.pessoa_monitorada_id.in_(pessoas_ids))
        .order_by(TelemetriaEvento.data_evento.desc(), TelemetriaEvento.id.desc())
        .limit(20)
        .all()
    )

    return [
        TelemetriaEventoResponse(
            id=evento.id,
            mac_address=evento.mac_address,
            tipo_evento=evento.tipo_evento,
            coordenadas_gps=evento.coordenadas_gps,
            data_evento=evento.data_evento,
            pessoa_monitorada_nome=nome,
        )
        for evento, nome in eventos
    ]


@router.post("", response_model=TelemetriaEventoResponse, status_code=201)
def cadastrar_evento_telemetria(
    payload: TelemetriaEventoPayload,
    authorization: str = Header(..., description="Bearer <token>"),
    db: Session = Depends(get_db),
):
    usuario = _obter_usuario_autenticado(authorization, db)
    pulseira = (
        db.query(Pulseira, PessoaMonitorada.nome_completo)
        .outerjoin(PessoaMonitorada, PessoaMonitorada.id == Pulseira.pessoa_monitorada_id)
        .filter(
            Pulseira.mac_address == payload.mac_address.strip(),
            Pulseira.pessoa_monitorada_id.in_(
                select(PessoaMonitorada.id).filter(
                    PessoaMonitorada.usuario_responsavel_id == usuario.id
                )
            ),
        )
        .first()
    )

    if not pulseira:
        raise HTTPException(status_code=404, detail="Pulseira não encontrada.")

    pulseira_db, nome = pulseira
    novo_evento = TelemetriaEvento(
        mac_address=pulseira_db.mac_address,
        tipo_evento=payload.tipo_evento.strip(),
        coordenadas_gps=payload.coordenadas_gps.strip() if payload.coordenadas_gps else None,
    )
    db.add(novo_evento)
    db.commit()
    db.refresh(novo_evento)

    return TelemetriaEventoResponse(
        id=novo_evento.id,
        mac_address=novo_evento.mac_address,
        tipo_evento=novo_evento.tipo_evento,
        coordenadas_gps=novo_evento.coordenadas_gps,
        data_evento=novo_evento.data_evento,
        pessoa_monitorada_nome=nome,
    )
