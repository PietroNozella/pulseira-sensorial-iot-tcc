# Gerenciador Wi-Fi e Cliente HTTP/REST

import network
import urequests
import ujson
import time
import os
import config
import provisionamento

class GerenciadorRede:
    def __init__(self, motor_pin):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.motor_pin = motor_pin
        self.ssid = None
        self.password = None

    def _carregar_credenciais_salvas(self): # Verifica se o arquivo de configuração existe na memória
        try:
            if "wifi_config.json" in os.listdir():
                with open("wifi_config.json", "r") as f:
                    dados = ujson.load(f)
                    self.ssid = dados.get("ssid")
                    self.password = dados.get("password")
                    return True
        except Exception as e:
            print("[REDE] Erro ao ler wifi_config.json:", e)
        return False

    def conectar_wifi(self):
        # Caso não tenha credenciais salvas, entra em modo AP para o App configurar
        if not self._carregar_credenciais_salvas():
            # print("Nenhuma configuração Wi-Fi encontrada")
            provisionamento.iniciar_modo_configuracao(self.motor_pin)
            return False

        # Tenta conectar na rede salva
        if not self.wlan.isconnected():
            # print(f"Conectando a rede salva: {self.ssid}")
            self.wlan.connect(self.ssid, self.password)
            
            tentativas = 0
            while not self.wlan.isconnected() and tentativas < 15: #tenta 15 vezes
                time.sleep_ms(500)
                tentativas += 1
                
        if self.wlan.isconnected():
            # print("Wi-Fi Conectado com sucesso IP:", self.wlan.ifconfig()[0])
            return True
        else:
            print("Falha ao conectar")
            # Se falhar muitas vezes, deleta o arquivo ruim e chama o modo de config novamente 
            os.remove("wifi_config.json")
            provisionamento.iniciar_modo_configuracao(self.motor_pin)
            return False

    def enviar_alerta_queda(self, vetor_g_pico, pitch, roll):
        if not self.conectar_wifi():
            return False

        payload = {
            "id_dispositivo": config.ID_DISPOSITIVO,
            "tipo_evento": "QUEDA_CONFIRMADA",
            "aceleracao_g": round(vetor_g_pico, 2),
            "pitch_final": round(pitch, 2),
            "roll_final": round(roll, 2),
            "status": "EMERGENCIA",
            "timestamp_local": time.time()
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": config.TOKEN_SEGURANCA
        }

        print("Disparando alerta e dados angulares para o servidor")
        try:
            resposta = urequests.post(
                config.API_URL, 
                data=ujson.dumps(payload), 
                headers=headers
            )
            print(f"Resposta do Servidor: HTTP {resposta.status_code}")
            resposta.close()
            return True
        except Exception as e:
            print("Falha ao enviar requisição HTTP POST:", e)
            return False