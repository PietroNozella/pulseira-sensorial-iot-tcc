# FallSense

Sistema completo de **detecção de quedas** para idosos — pulseira IoT, backend e aplicativo móvel para cuidadores e familiares.

**Integrantes:**
- Pietro Nozella
- Gustavo Quintiliano
- Diego Alves
- Bruno Shiraishi

---

## Arquitetura

O ecossistema é composto por três camadas:

- **Dispositivo wearable** — XIAO ESP32-C3 + MPU6050
- **Backend API** — Python com FastAPI + PostgreSQL
- **Aplicativo móvel** — destinado a cuidadores e familiares

**Comunicação:**
- MQTT sobre TLS entre dispositivo e backend
- HTTPS com JWT entre aplicativo e API

---

## Detecção de Quedas (2 etapas)

A lógica de detecção ocorre no firmware do dispositivo, em duas etapas sequenciais:

1. **Detecção de Impacto (SVM)** — leitura contínua do acelerômetro e cálculo do Signal Vector Magnitude:
   - `SVM = √(x² + y² + z²)`
   - Possível evento crítico quando SVM > **2,5G**

2. **Confirmação de Postura (Trigonometria)** — após impacto > 2,5G, análise de angulação (Pitch e Roll) para confirmar queda horizontal.

3. **Janela de cancelamento** — alerta enviado após **10 segundos** para permitir que o usuário cancele um falso positivo.

---

## Hardware

- **Microcontrolador:** XIAO ESP32-C3
- **Acelerômetro:** MPU6050 (via I2C)
- Fonte/bateria
- Opcionais: buzzer, LED

**Pinagem (I2C) — XIAO ESP32-C3:**

| Sinal | GPIO |
|-------|------|
| **SDA** | GPIO 6 |
| **SCL** | GPIO 7 |

---

## Segurança

- Senhas com **Argon2id**
- **2FA** via TOTP
- Controle de sessões com **JWT**
- Bloqueio temporário após múltiplas tentativas falhas
- Secure Boot e Flash Encryption no dispositivo
- Conformidade com **LGPD** (consentimento, minimização e retenção de dados)

---

## Estrutura do Projeto

```
fallsense_backend/   — API FastAPI (autenticação, 2FA, PostgreSQL)
```
