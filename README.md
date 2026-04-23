# FallSense — Sistema de Detecção de Quedas para Idosos

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=flat-square&logo=fastapi&logoColor=white)
![Flutter](https://img.shields.io/badge/Flutter-Mobile-02569B?style=flat-square&logo=flutter&logoColor=white)
![Dart](https://img.shields.io/badge/Dart-3.10-0175C2?style=flat-square&logo=dart&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E?style=flat-square&logo=supabase&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?style=flat-square&logo=docker&logoColor=white)
![ESP32--C3](https://img.shields.io/badge/ESP32--C3-IoT-E7352C?style=flat-square&logo=espressif&logoColor=white)
![MQTT](https://img.shields.io/badge/MQTT-TLS-660066?style=flat-square&logo=mqtt&logoColor=white)

Sistema integrado de detecção de quedas composto por pulseira IoT, backend API e aplicativo móvel. Desenvolvido como Trabalho de Conclusão de Curso.

**Equipe:** Pietro Nozella, Gustavo Quintiliano, Diego Alves e Bruno Shiraishi

---

## Sumário

- [Arquitetura](#arquitetura)
- [Estrutura do Repositório](#estrutura-do-repositório)
- [Hardware](#hardware)
- [Algoritmo de Detecção de Quedas](#algoritmo-de-detecção-de-quedas)
- [Backend](#backend)
  - [Tecnologias](#tecnologias)
  - [Endpoints da API](#endpoints-da-api)
  - [Modelos de Banco de Dados](#modelos-de-banco-de-dados)
  - [Segurança](#segurança)
  - [Como Rodar](#como-rodar)
- [Conformidade LGPD](#conformidade-lgpd)

---

## Arquitetura

O sistema é composto por três camadas que se comunicam entre si:

```
┌─────────────────┐        MQTT/TLS        ┌─────────────────────┐
│  Pulseira IoT   │ ─────────────────────► │   Backend FastAPI   │
│  XIAO ESP32-C3  │                        │   PostgreSQL        │
│  MPU6050        │                        │   Supabase          │
└─────────────────┘                        └──────────┬──────────┘
                                                      │ HTTPS + JWT
                                           ┌──────────▼──────────┐
                                           │   Aplicativo Móvel  │
                                           │   Flutter           │
                                           └─────────────────────┘
```

---

## Estrutura do Repositório

```
pulseira-sensorial-iot-tcc/
└── FallSense_Pulseira/
    └── Backend/
        ├── main.py                   # Entrypoint da API FastAPI
        ├── requirements.txt          # Dependências Python
        ├── Dockerfile                # Containerização
        ├── .env.example              # Exemplo de variáveis de ambiente
        ├── SECURITY.md               # Documentação técnica de segurança
        ├── testar_hash.py            # Script de teste do Argon2id
        ├── teste_cofre.py            # Script de teste da criptografia Fernet
        ├── models/
        │   └── user.py               # Modelos SQLAlchemy (User, LogAuditoria, tokens)
        ├── routers/
        │   ├── auth.py               # Endpoints de autenticação
        │   └── recuperacao.py        # Endpoints de recuperação de senha
        ├── schemas/
        │   └── auth_schemas.py       # Validação de entrada com Pydantic
        ├── security/
        │   ├── hashing.py            # Hash de senhas com Argon2id
        │   ├── crypto_vault.py       # Criptografia simétrica com Fernet
        │   ├── jwt_handler.py        # Emissão e validação de JWT
        │   ├── totp_handler.py       # Autenticação 2FA com TOTP
        │   └── database.py           # Configuração do SQLAlchemy
        └── tests/
            ├── test_auth.py          # Testes de autenticação
            └── test_recuperacao.py   # Testes de recuperação de senha
```

---

## Hardware

| Componente | Especificação |
|------------|---------------|
| Microcontrolador | XIAO ESP32-C3 |
| Sensor de movimento | MPU6050 (acelerômetro + giroscópio) |
| Protocolo I2C | SDA → GPIO 6 / SCL → GPIO 7 |
| Comunicação | MQTT sobre TLS |
| Segurança de firmware | Secure Boot + Flash Encryption |

---

## Algoritmo de Detecção de Quedas

A detecção ocorre em duas fases executadas diretamente no firmware da pulseira:

### Fase 1 — Detecção de Impacto

Calcula o Signal Vector Magnitude (SVM) continuamente a partir dos três eixos do acelerômetro:

```
SVM = √(x² + y² + z²)
```

Quando o SVM ultrapassa **2.5G**, o evento é sinalizado como possível queda.

### Fase 2 — Confirmação de Postura

Após o impacto, os ângulos de pitch e roll são calculados via trigonometria para verificar se o corpo assumiu posição horizontal, confirmando a queda.

### Janela de Cancelamento

Após a detecção, uma janela de **10 segundos** permite que o usuário cancele o alerta manualmente — evitando falsos positivos e notificações desnecessárias para cuidadores.

```
Impacto detectado (SVM > 2.5G)
        ↓
Verificação de postura (pitch/roll)
        ↓
Janela de cancelamento: 10 segundos
        ↓
Notificação enviada ao cuidador
```

---

## Backend

### Tecnologias

| Categoria | Tecnologia |
|-----------|-----------|
| Framework | FastAPI 0.135 |
| Banco de Dados | PostgreSQL via Supabase |
| ORM | SQLAlchemy |
| Validação | Pydantic v2 |
| Hash de Senhas | argon2-cffi (Argon2id) |
| Criptografia | cryptography (Fernet/AES-128) |
| Autenticação | PyJWT (HS256) |
| 2FA | pyotp (TOTP / RFC 6238) |
| Email | Brevo API |
| Containerização | Docker |

---

### Endpoints da API

Todos os endpoints estão sob o prefixo `/auth`.

#### Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/auth/registrar` | Cria novo usuário, gera segredo TOTP e 8 recovery codes |
| `POST` | `/auth/login` | Autentica com email, senha e código 2FA. Retorna JWT |
| `POST` | `/auth/logout` | Revoga o token JWT (blacklist) |

#### Recuperação de Senha

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/auth/esqueci-senha` | Gera token de 6 dígitos e envia por email via Brevo |
| `POST` | `/auth/resetar-senha` | Valida token e atualiza senha com novo hash Argon2id |

#### Utilitários

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/teste-banco` | Verifica conectividade com o banco de dados |
| `GET` | `/logs-auditoria` | Retorna os 10 registros mais recentes do log de auditoria |

---

### Modelos de Banco de Dados

#### `usuarios_api`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK | Identificador único |
| `email` | String UNIQUE | Email do usuário |
| `hashed_password` | String | Hash Argon2id da senha |
| `totp_secret` | String | Segredo TOTP para 2FA |
| `is_2fa_enabled` | Boolean | 2FA ativado (padrão: true) |
| `recovery_codes_hash` | String | JSON com hashes Argon2id dos 8 recovery codes |
| `failed_attempts` | Integer | Contador de tentativas de login falhas |
| `lockout_until` | Float | Timestamp Unix de desbloqueio da conta |
| `created_at` | DateTime | Data de criação |

#### `logs_auditoria`
| Campo | Descrição |
|-------|-----------|
| `usuario_id` | FK para o usuário (nullable) |
| `acao` | Ação registrada (ex: `LOGIN`, `LOGOUT`, `RECUPERACAO_SENHA_RESET`) |
| `descricao` | Detalhes da ação |
| `data_hora` | Timestamp automático |
| `status` | `SUCESSO` ou `FALHA` |

#### `tokens_revogados`
Blacklist de tokens JWT invalidados via logout. Impede reuso do token mesmo dentro do prazo de validade.

#### `tokens_recuperacao`
Armazena tokens temporários de recuperação de senha com flag `usado` e campo de `expiracao`.

---

### Segurança

#### Hash de Senhas — Argon2id

```python
PasswordHasher(
    time_cost=3,       # 3 iterações
    memory_cost=65536, # 64 MB de RAM por hash
    parallelism=4,     # 4 threads paralelas
    hash_len=32,       # digest de 256 bits
    salt_len=16        # salt aleatório de 128 bits
)
```

Salt gerado automaticamente e embutido na string resultante. Senhas nunca armazenadas em texto plano.

#### Criptografia Simétrica — Fernet (AES-128-CBC + HMAC-SHA256)

Dados sensíveis que precisam ser recuperados (ex: segredo TOTP) são criptografados com Fernet antes de persistir no banco. A chave mestra vem exclusivamente do `.env`.

#### JWT — HS256

Tokens com expiração de 60 minutos, assinados com `JWT_SECRET`. Logout insere o token na tabela `tokens_revogados` — qualquer uso posterior é rejeitado mesmo que o token ainda não tenha expirado.

#### 2FA — TOTP (RFC 6238)

Segredo de 160 bits gerado com `pyotp.random_base32()`. Código válido por 30 segundos, compatível com Google Authenticator e Authy.

#### Recovery Codes

8 códigos de recuperação gerados com `secrets.token_hex(4)` no momento do registro. Retornados ao usuário uma única vez. Armazenados no banco apenas como hashes Argon2id.

#### Proteção Contra Força Bruta

- Máximo de **3 tentativas** de login (senha ou 2FA)
- Bloqueio de **5 minutos** após exceder o limite
- Desbloqueio automático por timestamp — sem necessidade de job agendado

#### Validação de Senha

Senhas rejeitadas antes do hash se não atenderem:
- Mínimo de 8 caracteres
- Pelo menos 1 letra
- Pelo menos 1 número
- Pelo menos 1 caractere especial (`!@#$%^&*...`)

#### Recuperação de Senha

- Token de 6 dígitos gerado com `secrets.choice` (gerador criptograficamente seguro)
- Expiração de **15 minutos**
- Uso único — flag `usado=True` após consumo
- Resposta genérica independente do email existir (evita user enumeration)

---

### Como Rodar

#### Pré-requisitos

- Python 3.11+
- PostgreSQL (ou conta no Supabase)
- Conta na Brevo (para envio de emails)

#### Instalação

```bash
# Clone o repositório
git clone https://github.com/PietroNozella/pulseira-sensorial-iot-tcc.git
cd pulseira-sensorial-iot-tcc/FallSense_Pulseira/Backend

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Instale as dependências
pip install -r requirements.txt
```

#### Configuração do `.env`

Crie um arquivo `.env` na pasta `Backend/` com base no `.env.example`:

```env
# Banco de Dados
DATABASE_URL=postgresql://usuario:senha@host:5432/fallsense

# Segurança
JWT_SECRET=sua_chave_secreta_de_32_caracteres_aqui
ENCRYPTION_KEY=chave_fernet_gerada_pelo_comando_abaixo

# Email (Brevo)
BREVO_API_KEY=sua_api_key_brevo
```

Para gerar a `ENCRYPTION_KEY`:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

#### Executando

```bash
uvicorn main:app --reload
```

A API estará disponível em `http://localhost:8000`.
Documentação interativa: `http://localhost:8000/docs`

#### Testes

```bash
pytest tests/
```

#### Docker

```bash
docker build -t fallsense-backend .
docker run -p 8000:8000 --env-file .env fallsense-backend
```

---

## Conformidade LGPD

| Princípio | Implementação |
|-----------|---------------|
| **Minimização de dados** | Apenas dados necessários ao funcionamento são coletados |
| **Consentimento** | Usuário autoriza coleta no cadastro |
| **Segurança** | Dados sensíveis criptografados com Fernet antes de persistir |
| **Rastreabilidade** | Log de auditoria registra todas as ações críticas |
| **Retenção** | Política de exclusão de dados definida por prazo |

---

## Licença

Projeto acadêmico desenvolvido para fins de TCC. Todos os direitos reservados aos autores.
