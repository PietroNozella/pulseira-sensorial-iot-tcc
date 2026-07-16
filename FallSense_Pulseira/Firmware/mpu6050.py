# Driver I2C nativo para leitura

# 0x68 = endereço I2C padrão do chip MPU-6050
# 0x6B = endereço de memória interna do registrador PWR_MGMT_1
# 0x00 = comando para ligar o sensor e tirá-lo do modo de economia de energia
# 0x8000 = número 32.768, usado pelo código para verificar se o valor que saiu do sensor é um número negativo
# 0x3B = gaveta de memória onde fica salva a leitura da Aceleração no Eixo X
# 0x3D = gaveta de memória onde fica salva a leitura da Aceleração no Eixo Y
# 0x3F = gaveta de memória onde fica salva a leitura da Aceleração no Eixo Z


from machine import I2C
import time

class MPU6050:
    def __init__(self, i2c, endereco=0x68):
        self.i2c = i2c
        self.end = endereco
        self._acordar_sensor()

    def _acordar_sensor(self): # Escreve 0x00 no registrador (0x6B) para acordar o sensor
        try:
            self.i2c.writeto_mem(self.end, 0x6B, b'\x00')
            time.sleep_ms(50)
        except Exception as e:
            print("[ERRO I2C] Falha ao comunicar com o MPU-6050:", e)

    def _ler_inteiro_16bit(self, registrador):
        bytes_lidos = self.i2c.readfrom_mem(self.end, registrador, 2)
        valor = (bytes_lidos[0] << 8) | bytes_lidos[1]
        if valor & 0x8000:
            valor -= 65536
        return valor

    def ler_aceleracao_g(self): # Converte para escala G, escala padrão +/- 2G = 16384 LSB/G
        x = self._ler_inteiro_16bit(0x3B) / 16384.0
        y = self._ler_inteiro_16bit(0x3D) / 16384.0
        z = self._ler_inteiro_16bit(0x3F) / 16384.0
        return x, y, z