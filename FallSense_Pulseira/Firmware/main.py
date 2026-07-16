from machine import Pin, I2C
import time
import config
from mpu6050 import MPU6050
from algoritmo import DetectorQueda, EstadoQueda
from rede import GerenciadorRede


# Pinos de Interface
botao = Pin(config.PIN_BOTAO, Pin.IN, Pin.PULL_UP)  # Pressionado = 0
motor = Pin(config.PIN_MOTOR, Pin.OUT)
motor.value(0)


# Barramento I2C e Sensores
i2c = I2C(0, sda=Pin(config.PIN_SDA), scl=Pin(config.PIN_SCL), freq=400000)
sensor = MPU6050(i2c)


# Exemplificação dos Módulos Lógicos
algoritmo = DetectorQueda()

# Passa o pino do motor para a rede poder vibrar durante o provisionamento
rede = GerenciadorRede(motor) 

# Verifica a rede logo ao ligar (caso seja a primeira vez, vai travar aqui esperando o App)
rede.conectar_wifi()

# Inicialização funcionou (Só chega aqui se o Wi-Fi já estiver conectado)
motor.value(1); time.sleep_ms(150)
motor.value(0); time.sleep_ms(100)
motor.value(1); time.sleep_ms(150)
motor.value(0)
# print("Wi-Fi OK, Monitoramento iniciado.\n")


# Gerencionamento de alerta
def executar_janela_alerta_ux(vetor_g_registrado, pitch_final, roll_final):
    # print("\nQueda confirmada, Janela de 10s para cancelamento")
    inicio_janela = time.ticks_ms()
    cancelado = False
    
    while time.ticks_diff(time.ticks_ms(), inicio_janela) < config.JANELA_CANCELAMENTO_MS:
        motor.value(1); time.sleep_ms(300); motor.value(0); time.sleep_ms(200)
        
        if botao.value() == 0:
            # print("Botão pressionado, Alerta de queda CANCELADO pelo usuário.")
            cancelado = True
            motor.value(1); time.sleep_ms(800); motor.value(0)
            break
            
    if not cancelado:
        # print("Tempo esgotado sem cancelamento. Disparando via API")
        motor.value(1)
        sucesso = rede.enviar_alerta_queda(vetor_g_registrado, pitch_final, roll_final)
        motor.value(0)

        '''
        if sucesso:
            print("Alerta entregue com sucesso aos familiares")
        else:
            print("Falha no envio. Armazenando no buffer local")
        '''

    algoritmo.resetar()
    # print("\nRetornando ao monitoramento continuo")



while True:
    try:
        ax, ay, az = sensor.ler_aceleracao_g()
        estado_atual, g_filtrado, pitch, roll = algoritmo.atualizar(ax, ay, az)
        
        print(f"VetorG:{round(g_filtrado,2)} Pitch:{round(pitch,1)} Roll:{round(roll,1)}")
        
        if estado_atual == EstadoQueda.QUEDA_DETECTADA:
            executar_janela_alerta_ux(g_filtrado, pitch, roll)
            
        time.sleep_ms(config.TAXA_AMOSTRAGEM_MS)
        
    except Exception as e:
        print("Erro: ", e)
        time.sleep_ms(1000)