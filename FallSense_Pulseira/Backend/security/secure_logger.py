import json
import hashlib
import os
from datetime import datetime

# Define o caminho absoluto da raiz do Backend de forma dinâmica
DIRETORIO_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Isola os arquivos de log em um diretório específico para facilitar o controle de acesso e evitar exposição indevida
DIRETORIO_LOG = os.path.join(DIRETORIO_BASE, "logs")
ARQUIVO_LOG = os.path.join(DIRETORIO_LOG, "audit_secure.log")

# Assegura a existência do diretório de destino antes da primeira operação de escrita
os.makedirs(DIRETORIO_LOG, exist_ok=True)


# Recupera a assinatura hash do último evento registrado.  Caso o arquivo esteja vazio ou não exista, retorna uma string de 64 zeros, estabelecendo o ponto de partida da cadeia criptográfica
def obter_ultimo_hash() -> str:
    if not os.path.exists(ARQUIVO_LOG):
        return "0" * 64
    
    try:
        with open(ARQUIVO_LOG, 'r', encoding='utf-8') as arquivo:
            linhas = arquivo.readlines()
            if not linhas:
                return "0" * 64
            
            # Deserializa a última entrada para extrair seu hash validador.
            ultimo_log = json.loads(linhas[-1])
            return ultimo_log.get("hash", "0" * 64)
    except Exception:
        # Fallback seguro para cenários de corrupção de leitura na inicialização.
        return "0" * 64


# Registra um novo evento no sistema, vinculando-o matematicamente ao evento anterior
def registrar_log_seguro(evento: str, usuario_id: str, detalhes: str) -> str:
    ultimo_hash = obter_ultimo_hash()
    
    # Estrutura base do payload de auditoria
    dados_log = {
        "data_hora": datetime.now().isoformat(),
        "evento": evento,
        "usuario_id": str(usuario_id),
        "detalhes": detalhes,
        "hash_anterior": ultimo_hash
    }
    
    # A serialização requer sort_keys=True para garantir o determinismo sem isso, chaves em ordens diferentes gerariam hashes distintos para os mesmos dados
    string_dados = json.dumps(dados_log, sort_keys=True)
    
    # Calcula o hash SHA-256, consolidando a integridade dos dados atuais e do elo anterior
    hash_atual = hashlib.sha256(string_dados.encode('utf-8')).hexdigest()
    
    # Anexa a assinatura digital ao registro final.
    entrada_log = dados_log.copy()
    entrada_log["hash"] = hash_atual
    
    # Garante que logs anteriores não sejam sobrescritos durante a operação I/O
    with open(ARQUIVO_LOG, 'a', encoding='utf-8') as arquivo:
        arquivo.write(json.dumps(entrada_log) + "\n")
        
    return hash_atual


# Executa uma varredura  em toda a trilha de auditoria para atestar sua integridade
def verificar_integridade_logs() -> tuple:
    if not os.path.exists(ARQUIVO_LOG):
        return True, "Arquivo de log vazio ou inexistente. Sistema íntegro."

    with open(ARQUIVO_LOG, 'r', encoding='utf-8') as arquivo:
        linhas = arquivo.readlines()

    # O ciclo inicia aguardando o Genesis Hash
    hash_anterior_esperado = "0" * 64
    
    for indice, linha in enumerate(linhas):
        try:
            entrada_log = json.loads(linha.strip())
            
            # Isola a assinatura armazenada e a remove do dicionário para recalcular a base
            hash_armazenado = entrada_log.pop("hash")
            
            # Aplica o mesmo algoritmo determinístico usado na gravação
            string_dados = json.dumps(entrada_log, sort_keys=True)
            hash_calculado = hashlib.sha256(string_dados.encode('utf-8')).hexdigest()
            
            # Detecção de adulteração de conteúdo (Data Tampering)
            if hash_calculado != hash_armazenado:
                return False, f"FALHA DE INTEGRIDADE: Adulteração detectada no payload da linha {indice + 1}."
            
            # Detecção de exclusão/reordenação (Chain Breaking).
            if entrada_log["hash_anterior"] != hash_anterior_esperado:
                return False, f"FALHA DE INTEGRIDADE: Quebra de encadeamento detectada na linha {indice + 1}."
            
            # Prepara o estado para a validação do próximo elo da corrente.
            hash_anterior_esperado = hash_armazenado
            
        except Exception as erro:
            return False, f"ERRO FORENSE: Falha crítica ao processar a linha {indice + 1}. Detalhe: {str(erro)}"
            
    return True, "SISTEMA ÍNTEGRO: Toda a cadeia de logs foi validada com sucesso."