# Parâmetros de Hardware, Rede, API, força G e Ângulos de Inclinação

# Config dos Pinos
PIN_SDA = 6       # D4 - Linha de Dados I2C
PIN_SCL = 7       # D5 - Linha de Clock I2C
PIN_BOTAO = 3     # D1 - Botão de Cancelamento
PIN_MOTOR = 4     # D2 - Motor de Vibração

# Parametros do algoritmo de detecção
LIMITE_QUEDA_LIVRE = 0.45   # Abaixo disso indica queda livre (< 0.45G)
LIMITE_IMPACTO = 2.40       # Acima disso indica choque com o solo
LIMITE_REPOUSO = 1.15       # Variação máxima para considerar imobilidade
LIMITE_VARIACAO_ANGULAR = 60.0 # Graus: Mudança mínima de inclinação (Pitch/Roll)
TEMPO_REPOUSO_MS = 2000     # Tempo imóvel após impacto para confirmar queda
JANELA_CANCELAMENTO_MS = 10000  # Janela de tempo para o idoso cancelar (10s)
TAXA_AMOSTRAGEM_MS = 50     # Leitura a cada 50ms

# Credencial de API
API_URL = "https://fallsense-api.onrender.com/telemetria"

#Import do env_hardware.py
try:
    import env_hardware
    WIFI_SSID = env_hardware.WIFI_SSID_LAB
    WIFI_PASS = env_hardware.WIFI_PASS_LAB
    TOKEN_SEGURANCA = env_hardware.API_BEARER_TOKEN
    ID_DISPOSITIVO = env_hardware.ID_DISPOSITIVO_GERADO
except ImportError:
    print("Arquivo 'env_hardware.py' não encontrado na memória do XIAO-ESP32")
    print("Por favor, crie baseando-se no arquivo 'env_hardware.py.example'")
    
    # Valores padrão de fallback caso o provisionamento ainda não tenha ocorrido
    WIFI_SSID = None
    WIFI_PASS = None
    TOKEN_SEGURANCA = ""
    ID_DISPOSITIVO = "XIAO_ESP32C3_PROV_PENDENTE"