# FallSense - Sistema de Deteccao de Quedas para Idosos

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=flat-square&logo=fastapi&logoColor=white)
![Flutter](https://img.shields.io/badge/Flutter-Mobile-02569B?style=flat-square&logo=flutter&logoColor=white)
![Dart](https://img.shields.io/badge/Dart-3.10-0175C2?style=flat-square&logo=dart&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E?style=flat-square&logo=supabase&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?style=flat-square&logo=docker&logoColor=white)

Sistema academico desenvolvido como TCC para monitoramento de quedas, com backend em FastAPI, aplicativo mobile em Flutter e documentacao complementar de seguranca, LGPD e QA.

**Equipe:** Pietro Nozella, Gustavo Quintiliano, Diego Alves e Bruno Shiraishi

## Visao Geral

O repositorio esta organizado em tres frentes principais:

- `FallSense_Pulseira/Backend`: API FastAPI com autenticacao, 2FA, recuperacao de senha, perfil, monitorados, pulseiras, telemetria e compliance.
- `FallSense_Pulseira/Frontend`: aplicativo Flutter com fluxo de login, cadastro, 2FA, home e perfil.
- `docs/`: materiais de apoio do projeto, incluindo relatorios tecnicos, LGPD, backlog e QA.

## Estrutura do Repositorio

```text
pulseira-sensorial-tcc/
|-- README.md
|-- RELATORIO_ESTUDO.md
|-- docs/
|   |-- backlogs-e-qa/
|   |-- documentacao-tecnico-cientifica/
|   |-- relatorios-lgpd/
|   |-- resumo-cientifico.md
|   `-- RELATORIO_APRESENTACAO_CODIGO.md
`-- FallSense_Pulseira/
    |-- Backend/
    |   |-- main.py
    |   |-- requirements.txt
    |   |-- Dockerfile
    |   |-- .env.example
    |   |-- SECURITY.md
    |   |-- assets/
    |   |-- models/
    |   |-- routers/
    |   |-- schemas/
    |   |-- security/
    |   `-- tests/
    `-- Frontend/
        |-- lib/
        |-- assets/
        |-- android/
        |-- ios/
        |-- web/
        `-- pubspec.yaml
```

## Arquitetura

O projeto atualmente versiona o backend, o frontend mobile e a documentacao academica. O firmware da pulseira e mencionado no contexto do TCC, mas nao esta presente neste repositorio.

Fluxo principal da aplicacao:

```text
Aplicativo Flutter
       |
       | HTTPS + JWT
       v
Backend FastAPI
       |
       | SQLAlchemy
       v
PostgreSQL / Supabase
```

## Backend

### Stack

| Categoria | Tecnologia |
|---|---|
| Linguagem | Python 3.11 |
| Framework | FastAPI 0.136.1 |
| Banco de dados | PostgreSQL |
| Persistencia | SQLAlchemy 2 |
| Validacao | Pydantic 2 |
| Autenticacao | JWT (HS256) |
| Segundo fator | TOTP |
| Hash de senha | Argon2id |
| Integracao de email | Brevo API |
| Containerizacao | Docker |

### Rotas atualmente expostas

#### Infra e utilitarios

| Metodo | Endpoint | Descricao |
|---|---|---|
| `GET` | `/health` | Verifica se a API esta ativa |
| `GET` | `/teste-banco` | Testa conectividade com o banco |
| `GET` | `/logs-auditoria` | Retorna os 10 logs mais recentes |

#### Autenticacao e conta

| Metodo | Endpoint | Descricao |
|---|---|---|
| `POST` | `/auth/registrar` | Cria usuario e retorna segredo TOTP e recovery codes |
| `POST` | `/auth/login` | Login com fluxo em duas etapas para 2FA |
| `POST` | `/auth/logout` | Revoga o token atual |
| `GET` | `/auth/me` | Retorna dados do perfil autenticado |
| `PATCH` | `/auth/me` | Atualiza nome, email e telefone |
| `PATCH` | `/auth/me/senha` | Atualiza a senha do usuario autenticado |
| `DELETE` | `/auth/me` | Exclui a conta autenticada |

#### Recuperacao de senha

| Metodo | Endpoint | Descricao |
|---|---|---|
| `POST` | `/auth/esqueci-senha` | Gera codigo de 6 digitos e envia por email |
| `POST` | `/auth/resetar-senha` | Valida token e redefine a senha |

#### Pessoas monitoradas

| Metodo | Endpoint | Descricao |
|---|---|---|
| `GET` | `/monitorados` | Lista pessoas monitoradas do usuario autenticado |
| `POST` | `/monitorados` | Cadastra uma nova pessoa monitorada |

#### Pulseiras

| Metodo | Endpoint | Descricao |
|---|---|---|
| `GET` | `/pulseiras` | Lista pulseiras vinculadas ao usuario |
| `POST` | `/pulseiras` | Cadastra uma pulseira para uma pessoa monitorada |

#### Telemetria

| Metodo | Endpoint | Descricao |
|---|---|---|
| `GET` | `/eventos` | Lista os eventos de telemetria mais recentes |
| `POST` | `/eventos` | Registra novo evento de telemetria |

#### Compliance

| Metodo | Endpoint | Descricao |
|---|---|---|
| `GET` | `/compliance/termos/download` | Faz download do PDF de termos de uso |

### Modelos principais

As entidades de dominio atualmente presentes em [models/user.py](/C:/Users/Micro/Desktop/pulseira-sensorial-tcc/FallSense_Pulseira/Backend/models/user.py:1) sao:

- `User`
- `LogAuditoria`
- `TokenRevogado`
- `TokenRecuperacao`
- `PessoaMonitorada`
- `Pulseira`
- `TelemetriaEvento`

### Seguranca

O backend implementa:

- hash de senha com Argon2id;
- autenticacao com JWT;
- 2FA com TOTP;
- bloqueio temporario apos tentativas de login invalidas;
- auditoria de eventos sensiveis;
- revogacao de token no logout;
- recuperacao de senha por token temporario;
- endpoint para distribuicao dos termos de uso.

Detalhes tecnicos adicionais estao em [SECURITY.md](/C:/Users/Micro/Desktop/pulseira-sensorial-tcc/FallSense_Pulseira/Backend/SECURITY.md:1).

### Como rodar o backend

#### Pre-requisitos

- Python 3.11+
- Banco PostgreSQL ou Supabase configurado
- Chave JWT
- Chave Fernet para criptografia
- Chave da Brevo para envio de email

#### Instalacao

```bash
git clone https://github.com/PietroNozella/pulseira-sensorial-iot-tcc.git
cd pulseira-sensorial-iot-tcc/FallSense_Pulseira/Backend

python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

#### Variaveis de ambiente necessarias

O arquivo `.env.example` do projeto esta incompleto em relacao ao que o backend exige hoje. Para executar a API, garanta pelo menos:

```env
DATABASE_URL=postgresql://usuario:senha@host:5432/fallsense
JWT_SECRET=sua_chave_jwt
ENCRYPTION_KEY=sua_chave_fernet
BREVO_API_KEY=sua_chave_brevo
```

Para gerar a `ENCRYPTION_KEY`:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

#### Executando

```bash
uvicorn main:app --reload
```

API local:

- `http://localhost:8000`
- `http://localhost:8000/docs`

#### Testes

```bash
pytest tests/
```

Os testes usam SQLite em memoria para isolar a suite do banco real.

#### Docker

```bash
docker build -t fallsense-backend .
docker run -p 8000:8000 --env-file .env fallsense-backend
```

## Frontend

O frontend foi desenvolvido em Flutter e contem telas e fluxos para:

- login;
- cadastro;
- recuperacao de senha;
- autenticacao em dois fatores;
- navegacao principal;
- home com listagem de dispositivos e eventos;
- perfil, edicao de perfil, troca de senha e exclusao de conta.

Dependencias relevantes do app:

- `flutter_riverpod`
- `http`
- `flutter_secure_storage`
- `qr_flutter`

Entrypoint principal:

- [lib/main.dart](/C:/Users/Micro/Desktop/pulseira-sensorial-tcc/FallSense_Pulseira/Frontend/lib/main.dart:1)

Arquivo de dependencias:

- [pubspec.yaml](/C:/Users/Micro/Desktop/pulseira-sensorial-tcc/FallSense_Pulseira/Frontend/pubspec.yaml:1)

## Documentacao Complementar

O repositorio tambem inclui materiais de apoio do projeto em `docs/`, com destaque para:

- backlog e QA em [docs/backlogs-e-qa/README.md](/C:/Users/Micro/Desktop/pulseira-sensorial-tcc/docs/backlogs-e-qa/README.md:1);
- relatorios de LGPD em `docs/relatorios-lgpd/`;
- documentacao tecnico-cientifica em `docs/documentacao-tecnico-cientifica/`;
- relatorio de apresentacao do codigo em [docs/RELATORIO_APRESENTACAO_CODIGO.md](/C:/Users/Micro/Desktop/pulseira-sensorial-tcc/docs/RELATORIO_APRESENTACAO_CODIGO.md:1).

## LGPD

O projeto possui artefatos especificos de conformidade e governanca em `docs/relatorios-lgpd/` e um endpoint dedicado para download dos termos de uso no backend.

## Licenca

Projeto academico desenvolvido para fins de TCC. Todos os direitos reservados aos autores.
