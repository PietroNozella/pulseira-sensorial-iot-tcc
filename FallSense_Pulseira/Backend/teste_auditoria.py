from security.secure_logger import registrar_log_seguro, verificar_integridade_logs
import time

print("INICIANDO SIMULAÇÃO DE AUDITORIA SEGURA...\n")

# 1. Simulando eventos normais do sistema
print("Gravando eventos no sistema...")
hash1 = registrar_log_seguro("LOGIN_SUCESSO", "user_123", "IP: 192.168.0.5")
time.sleep(0.5) # Pequena pausa para os timestamps ficarem diferentes
hash2 = registrar_log_seguro("ALERTA_QUEDA", "user_123", "Aceleração brusca detectada pelo ESP32-C3.")
time.sleep(0.5)
hash3 = registrar_log_seguro("CANCELAMENTO_BOTAO", "user_123", "Usuário cancelou o alerta.")

print(f"Último Hash Gerado: {hash3[:15]}...\n")

# 2. Verificando a integridade (Sem alterações)
print("🔍 VARREDURA FORENSE (Antes do Ataque):")
status, mensagem = verificar_integridade_logs()
print(mensagem, "\n")