# Modo AP e Servidor Web local para o App Flutter

import network
import socket
import ujson
import time
import machine

ARQUIVO_CONFIG = "wifi_config.json"
SSID_AP = "FallSense_Setup"

def iniciar_modo_configuracao(motor_pin):
    # Criar a rede Wi-Fi da própria pulseira
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=SSID_AP, authmode=0) # Rede aberta para facilitar
    
    ip_ap = ap.ifconfig()[0]
    '''
    para teste: 
    print(f"Rede '{SSID_AP}' criada com sucesso!")
    print(f"Aguardando conexão do App Flutter no IP: {ip_ap}:80")
    '''

    # Vibração dupla rápida para avisar que está em modo de configuração
    motor_pin.value(1); time.sleep_ms(100); motor_pin.value(0); time.sleep_ms(100)
    motor_pin.value(1); time.sleep_ms(100); motor_pin.value(0)



    # Criar um servidor HTTP na porta 80
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(('', 80))
    servidor.listen(1)



    while True:
        try:
            # Pisca o motor levemente a cada 3 segundos para mostrar que está aguardando
            conexao, endereco = servidor.accept()
            requisicao = conexao.recv(1024).decode('utf-8')
            
            # caso o App enviou as credenciais via POST
            if "POST /config" in requisicao: # Extrai o JSON do corpo da requisição HTTP
                corpo = requisicao.split('\r\n\r\n')[1]
                dados_wifi = ujson.loads(corpo)
                
                ssid_recebido = dados_wifi.get("ssid")
                pass_recebido = dados_wifi.get("password")
                
                if ssid_recebido and pass_recebido:
                   # print(f"Credenciais recebidas para a rede: {ssid_recebido}")
                    
                    # Salvar permanentemente na memória da pulseira
                    with open(ARQUIVO_CONFIG, "w") as f:
                        ujson.dump({"ssid": ssid_recebido, "password": pass_recebido}, f)
                    
                    # Resposta de Sucesso para o App Flutter
                    resposta = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\":\"sucesso\"}"
                    conexao.send(resposta.encode('utf-8'))
                    conexao.close()
                    servidor.close()
                    ap.active(False)
                    
                    # print("Configuração salva, Reiniciando a pulseira em 2s")
                    motor_pin.value(1); time.sleep_ms(500); motor_pin.value(0)
                    time.sleep(2)
                    machine.reset() # Reinicia o ESP32 para conectar na rede nova
                    
            # Resposta padrão se tentarem acessar via navegador comum
            resposta_html = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>FallSense Setup</h1><p>Use o aplicativo para configurar esta pulseira</p>"
            conexao.send(resposta_html.encode('utf-8'))
            conexao.close()
            
        except Exception as e:
            print("Erro: ", e)
            time.sleep_ms(100)