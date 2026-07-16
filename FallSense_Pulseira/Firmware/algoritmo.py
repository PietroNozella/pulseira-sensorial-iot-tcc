# Vetores G + Pitch & Roll

import math
import time
import config

class EstadoQueda:
    NORMAL = 0
    QUEDA_LIVRE = 1
    IMPACTO = 2
    CONFIRMANDO_REPOUSO = 3
    QUEDA_DETECTADA = 4

class DetectorQueda:
    def __init__(self):
        self.estado = EstadoQueda.NORMAL
        self.vetor_g_filtrado = 1.0
        self.tempo_inicio_estado = 0
        
        # Historico angular para comparar a inclinação antes e depois da queda
        self.pitch_inicial = 0.0
        self.roll_inicial = 0.0


    # Evitar divisão por zero se os eixos caírem exatamente em 0
    def _calcular_angulos(self, ax, ay, az): 
        try:
            pitch = math.atan(ax / math.sqrt(ay**2 + az**2)) * (180.0 / math.pi)
            roll = math.atan(ay / math.sqrt(ax**2 + az**2)) * (180.0 / math.pi)
            return pitch, roll
        except ZeroDivisionError:
            return 0.0, 0.0

    def atualizar(self, ax, ay, az):
        # Cálculo do Vetor G e dos Ângulos de Balanço (Pitch) e Rolagem (Roll)
        vetor_bruto = math.sqrt(ax**2 + ay**2 + az**2)
        pitch_atual, roll_atual = self._calcular_angulos(ax, ay, az)
        
        # Filtro Exponencial (EMA) no Vetor Resultante
        self.vetor_g_filtrado = (self.vetor_g_filtrado * 0.7) + (vetor_bruto * 0.3)
        agora = time.ticks_ms()

        # Estados da queda
        if self.estado == EstadoQueda.NORMAL:
            if self.vetor_g_filtrado < config.LIMITE_QUEDA_LIVRE:
                self.estado = EstadoQueda.QUEDA_LIVRE
                self.tempo_inicio_estado = agora
                # Salva a orientação do braço ANTES de começar a cair!
                self.pitch_inicial = pitch_atual
                self.roll_inicial = roll_atual
                print(f"Queda livre (Pitch inicial: {round(self.pitch_inicial, 1)}°)")

        elif self.estado == EstadoQueda.QUEDA_LIVRE:
            if time.ticks_diff(agora, self.tempo_inicio_estado) > 800:
                self.resetar()  # Movimento brusco isolado
            elif self.vetor_g_filtrado > config.LIMITE_IMPACTO:
                self.estado = EstadoQueda.IMPACTO
                self.tempo_inicio_estado = agora
                print("Impacto com o solo detectado!")

        elif self.estado == EstadoQueda.IMPACTO:
            if time.ticks_diff(agora, self.tempo_inicio_estado) > 500:
                self.estado = EstadoQueda.CONFIRMANDO_REPOUSO
                self.tempo_inicio_estado = agora
                print("Analisando inclinação e imobilidade")

        elif self.estado == EstadoQueda.CONFIRMANDO_REPOUSO:
            if self.vetor_g_filtrado > config.LIMITE_REPOUSO:
                print("Movimento detectado (Paciente levantou). Alarme abortado.")
                self.resetar()

            elif time.ticks_diff(agora, self.tempo_inicio_estado) > config.TEMPO_REPOUSO_MS:
                # Verifica se a inclinação do corpo mudou drasticamente
                var_pitch = abs(pitch_atual - self.pitch_inicial)
                var_roll = abs(roll_atual - self.roll_inicial)
                
                print(f"Variação Angular -> Pitch: {round(var_pitch,1)}° | Roll: {round(var_roll,1)}°")
                
                # Se o ângulo variou mais que 60 graus OU rolou muito na lateral, confirmar queda
                if var_pitch >= config.LIMITE_VARIACAO_ANGULAR or var_roll >= config.LIMITE_VARIACAO_ANGULAR:
                    self.estado = EstadoQueda.QUEDA_DETECTADA
                    print("Queda CONFIRMADA por impacto + rotação do corpo")
                else:
                    print("Alarme falso, Houve impacto, mas o braço continuou na mesma orientação.")
                    self.resetar()

        return self.estado, self.vetor_g_filtrado, pitch_atual, roll_atual

    def resetar(self):
        self.estado = EstadoQueda.NORMAL