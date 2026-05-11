# Relatório de Inventário de Dados

## 1. Identificação do projeto

**Projeto:** FallSense  
**Tipo de solução:** sistema de detecção de quedas para idosos com pulseira IoT, backend FastAPI e aplicativo Flutter  
**Base deste relatório:** análise do repositório em 04/05/2026

## 2. Objetivo do relatório

Este relatório tem como finalidade mapear, de forma clara e organizada, quais dados são tratados pelo projeto FallSense, de onde esses dados vêm, para que são usados, onde ficam armazenados e quais cuidados precisam existir para garantir conformidade com a LGPD.

Na prática, o inventário de dados funciona como uma fotografia do ciclo de vida das informações dentro do sistema.

## 3. Visão geral do tratamento de dados

O projeto trata dados em três frentes principais:

1. Dados do usuário responsável pela conta.
2. Dados da pessoa monitorada pela pulseira.
3. Dados técnicos e operacionais gerados pelo uso da pulseira e da API.

Além disso, o sistema também trata dados de autenticação, segurança e recuperação de acesso.

## 4. Inventário dos dados pessoais

| Categoria | Dado | Titular | Origem | Finalidade | Local de armazenamento | Sensibilidade |
|---|---|---|---|---|---|---|
| Cadastro | nome completo | usuário responsável | formulário de cadastro/perfil | identificar o usuário no sistema | tabela `usuarios_api` | pessoal comum |
| Cadastro | e-mail | usuário responsável | formulário de cadastro/login | autenticação, comunicação e recuperação de conta | tabela `usuarios_api`, `tokens_recuperacao`, logs | pessoal comum |
| Cadastro | telefone | usuário responsável | formulário de cadastro/perfil | contato e composição do perfil | tabela `usuarios_api` | pessoal comum |
| Credencial | senha | usuário responsável | formulário de cadastro/login | autenticação | não fica em texto puro; somente hash em `usuarios_api` | dado sigiloso de autenticação |
| Segurança | segredo TOTP | usuário responsável | gerado pelo backend no registro | segundo fator de autenticação | tabela `usuarios_api` | dado sigiloso de autenticação |
| Segurança | códigos de recuperação | usuário responsável | gerados no registro | contingência de acesso | somente hash em `usuarios_api` | dado sigiloso de autenticação |
| Sessão | token JWT | usuário responsável | gerado no login | manter sessão autenticada | app móvel e tabela `tokens_revogados` quando houver logout | dado sigiloso de autenticação |
| Recuperação de conta | token de reset | usuário responsável | gerado no fluxo de recuperação | redefinir senha | tabela `tokens_recuperacao` | dado sigiloso de autenticação |
| Perfil monitorado | nome completo | pessoa monitorada | cadastro feito pelo responsável | identificar a pessoa assistida | tabela `pessoa_monitorada` | pessoal comum |
| Vinculação LGPD | data de consentimento | pessoa monitorada | deveria ser registrada no fluxo de cadastro | comprovar consentimento | campo `consentimento_lgpd_data` | dado de governança LGPD |
| Dispositivo | MAC address da pulseira | pessoa monitorada/usuário vinculado | cadastro da pulseira | identificar dispositivo e associar eventos | tabela `pulseira` | dado técnico vinculável a pessoa |
| Dispositivo | versão do firmware | dispositivo | cadastro/integração | gestão técnica do hardware | tabela `pulseira` | dado técnico |
| Telemetria | tipo de evento | pessoa monitorada | pulseira/backend | registrar alerta, queda ou evento operacional | tabela `telemetria_evento` | potencialmente sensível por contexto |
| Telemetria | coordenadas GPS | pessoa monitorada | pulseira/backend | localização em caso de evento | tabela `telemetria_evento` | dado pessoal sensível na prática |
| Telemetria | data e hora do evento | pessoa monitorada | backend | rastreabilidade do evento | tabela `telemetria_evento` | dado contextual |
| Auditoria | ação realizada | usuário responsável | backend | trilha de auditoria | tabela `logs_auditoria` | dado operacional |
| Auditoria | descrição da ação | usuário responsável | backend | detalhamento para rastreabilidade | tabela `logs_auditoria` | pode conter dado pessoal |
| Auditoria | status da ação | usuário responsável | backend | segurança e monitoramento | tabela `logs_auditoria` | dado operacional |

## 5. Dados não pessoais ou predominantemente técnicos

O sistema também trata dados que, isoladamente, não são necessariamente pessoais, mas podem se tornar pessoais quando associados a um titular:

| Dado | Observação |
|---|---|
| `failed_attempts` | contador de falhas de login por usuário |
| `lockout_until` | bloqueio temporário por segurança |
| `status_ativo` da pulseira | indica se o dispositivo está ativo |
| timestamps de criação e registro | ajudam em auditoria e suporte |

## 6. Fluxo resumido de entrada dos dados

### 6.1 Cadastro do usuário

O usuário responsável informa nome, e-mail, telefone e senha. Nesse momento, o backend também gera dados complementares de segurança, como segredo TOTP e códigos de recuperação.

### 6.2 Cadastro da pessoa monitorada

Após autenticação, o usuário responsável pode cadastrar a pessoa que será acompanhada pela pulseira. Atualmente o campo efetivamente usado é o nome completo.

### 6.3 Cadastro da pulseira

A pulseira é vinculada a uma pessoa monitorada por meio do MAC address e, opcionalmente, da versão do firmware.

### 6.4 Registro de eventos

Quando ocorre um evento relevante, o sistema grava o tipo do evento, o identificador da pulseira, a data/hora e, se houver, coordenadas GPS.

## 7. Finalidades do tratamento

As finalidades identificadas no projeto são:

1. Permitir autenticação segura do responsável.
2. Permitir cadastro e gestão de perfis monitorados.
3. Vincular pulseiras físicas a pessoas monitoradas.
4. Registrar eventos de queda e alertas relacionados.
5. Permitir rastreabilidade e investigação de ações críticas.
6. Viabilizar recuperação de conta e suporte operacional.

## 8. Base legal sugerida por grupo de dados

Este item deve ser validado juridicamente, mas tecnicamente o enquadramento mais coerente hoje seria:

| Tratamento | Base legal sugerida |
|---|---|
| cadastro do usuário responsável | execução de procedimentos preliminares e execução de contrato/uso do serviço |
| autenticação e segurança da conta | legítimo interesse e proteção do crédito/segurança, conforme interpretação aplicável |
| recuperação de senha | legítimo interesse e segurança do titular |
| cadastro da pessoa monitorada | consentimento do titular ou de representante legal, conforme o caso |
| geolocalização e eventos de queda | proteção da vida e da incolumidade física; em alguns cenários também consentimento |
| logs de auditoria | legítimo interesse, segurança e prevenção a fraudes |

## 9. Compartilhamento de dados identificado

| Destino | Dados envolvidos | Motivo |
|---|---|---|
| Supabase/PostgreSQL | quase todos os dados persistidos | banco principal do sistema |
| Brevo | e-mail do usuário e token de recuperação | envio de e-mail de recuperação |
| aplicativo móvel | token JWT, nome do usuário | manter sessão e personalização básica |

## 10. Retenção de dados

O repositório menciona preocupação com retenção, mas não foi identificado no código um mecanismo completo e automatizado de política de retenção para:

1. logs de auditoria;
2. eventos de telemetria;
3. tokens revogados antigos;
4. tokens de recuperação expirados.

Por isso, a retenção hoje deve ser considerada **parcialmente definida em documentação, mas não totalmente implementada no código**.

## 11. Pontos de atenção encontrados no estado atual do projeto

Durante a análise do código, foram identificados pontos relevantes para constar no relatório de forma honesta:

1. O campo `consentimento_lgpd_data` existe no modelo da pessoa monitorada, mas não está sendo preenchido no fluxo atual de cadastro.
2. O segredo TOTP é descrito na documentação de segurança como criptografado, mas no código analisado ele é persistido diretamente no banco sem uma etapa visível de criptografia.
3. O token de recuperação de senha é armazenado em formato utilizável no banco, e não em hash.
4. O endpoint `/logs-auditoria` retorna logs recentes sem autenticação aparente.
5. O backend está com `allow_origins=["*"]`, o que é conveniente em desenvolvimento, mas pede revisão para produção.
6. As descrições do log de auditoria podem conter e-mail do usuário, o que amplia a exposição de dados pessoais dentro dos próprios logs.

## 12. Conclusão

O projeto FallSense já possui uma base técnica relevante de segurança e organização de dados, especialmente em autenticação, hash de senha, controle de sessão e trilha de auditoria. Ao mesmo tempo, por tratar dados ligados a monitoramento de idosos, geolocalização e eventos de possível queda, o sistema exige um cuidado elevado com minimização, consentimento, retenção e proteção adicional dos dados.

Este inventário mostra que o projeto já tem estrutura suficiente para documentação LGPD, mas também evidencia ajustes importantes antes de uma versão produtiva ou de apresentação institucional mais formal.
