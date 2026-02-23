# pulseira-sensorial-iot-tcc

**O Projeto:** Pulseira de **detecção de quedas** com **ESP32** e **MicroPython**.

**Integrantes:**
- Pietro Nozella
- Gustavo Quintiliano
- Diego Alves
- Bruno Shiraishi

**Como Funciona:**
- **Leitura** — aquisição contínua do **acelerômetro** (ex.: **MPU6050**/MPU9250) via **I2C**.
- **Detecção de impacto** — algoritmo no **MicroPython** (threshold de aceleração ou queda livre) para identificar queda.
- **Alerta Wi-Fi** — envio de notificação (HTTP, MQTT ou similar) quando queda é detectada.

**Hardware:**
- **ESP32**
- Módulo **acelerômetro** (MPU6050 ou equivalente)
- Fonte/bateria
- Opcionais: buzzer, LED

**Pinagem (I2C):**

| Sinal | Pino ESP32 |
|-------|------------|
| **SDA** | GPIO 21 |
| **SCL** | GPIO 22 |
