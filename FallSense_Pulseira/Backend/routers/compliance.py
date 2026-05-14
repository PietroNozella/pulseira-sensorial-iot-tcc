from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
import os
from security.secure_logger import registrar_log_seguro

# Cria o roteador para a documentação legal e compliance
router = APIRouter()

# Caminho dinâmico para encontrar a pasta "assets" na raiz do Backend
DIRETORIO_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQUIVO_TERMOS = os.path.join(DIRETORIO_BASE, "assets", "termos_de_uso.pdf")

# Endpoint para o Frontend baixar o PDF dos Termos de Uso e Privacidade da plataforma FallSense
@router.get("/termos/download", summary="Download dos Termos de Uso (LGPD)")
def baixar_termos_uso(usuario_id: str = Query("anonimo", description="ID do usuário que solicitou o download")):
    # Verifica se o arquivo físico existe no servidor
    if not os.path.exists(ARQUIVO_TERMOS):
        raise HTTPException(
            status_code=404, 
            detail="Arquivo de Termos de Uso não encontrado no servidor."
        )
    
    # Registra a trilha de quem baixou o documento
    registrar_log_seguro(
        evento="DOWNLOAD_TERMOS_USO",
        usuario_id=usuario_id,
        detalhes="Download do documento de Termos de Uso e Privacidade solicitado via API."
    )

    # Retorna o arquivo formatado para download automático
    return FileResponse(
        path=ARQUIVO_TERMOS, 
        filename="FallSense_Termos_de_Uso.pdf", # Nome que aparecerá para o usuário salvar
        media_type="application/pdf"
    )