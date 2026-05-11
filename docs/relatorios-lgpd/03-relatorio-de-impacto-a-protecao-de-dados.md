# Relatório de Impacto à Proteção de Dados Pessoais (RIPD)

## 1. Objetivo do RIPD

Este relatório avalia os riscos do tratamento de dados pessoais realizado pelo projeto FallSense, especialmente porque o sistema envolve monitoramento de pessoa potencialmente vulnerável, tratamento de geolocalização e registro de eventos ligados à integridade física.

O foco aqui não é apenas listar dados, mas entender:

1. por que o tratamento pode gerar risco;
2. quais controles já existem;
3. quais lacunas ainda precisam ser tratadas.

## 2. Escopo analisado

O relatório considera o estado atual do repositório, abrangendo:

1. backend FastAPI;
2. banco PostgreSQL/Supabase;
3. aplicativo Flutter;
4. integração de recuperação de senha por e-mail;
5. cadastro de pessoas monitoradas, pulseiras e telemetria.

## 3. Descrição resumida do tratamento

O FallSense foi concebido para permitir que um usuário responsável acompanhe uma pessoa monitorada por meio de uma pulseira inteligente capaz de registrar eventos associados a quedas. Para isso, o sistema trata:

1. dados cadastrais do responsável;
2. dados de autenticação e segurança;
3. nome da pessoa monitorada;
4. identificador da pulseira;
5. eventos e possível geolocalização associados à pulseira.

## 4. Por que este tratamento exige RIPD

Mesmo sem armazenar prontuário médico formal, o projeto trata informações que, pelo contexto, aumentam bastante o risco para o titular:

1. monitoramento de idoso ou pessoa potencialmente vulnerável;
2. eventos que podem indicar condição física ou emergência;
3. localização geográfica por coordenadas GPS;
4. associação entre dispositivo, rotina e identidade;
5. risco relevante em caso de acesso indevido ou vazamento.

Por isso, o tratamento deve ser considerado de impacto elevado em termos de privacidade e segurança.

## 5. Mapeamento de riscos por etapa

### 5.1 Cadastro e autenticação

**Risco principal:** comprometimento da conta do responsável, com acesso indireto aos dados da pessoa monitorada.

**Impacto possível:** acesso indevido à identidade da pessoa monitorada, seus eventos e sua localização.

**Controles existentes identificados:**

1. hash de senha com Argon2id;
2. autenticação em dois fatores;
3. bloqueio após tentativas falhas;
4. JWT com expiração;
5. revogação de token no logout.

**Risco residual:** médio.

### 5.2 Recuperação de senha

**Risco principal:** abuso do fluxo de reset, interceptação do código ou uso indevido do token.

**Impacto possível:** tomada de conta.

**Controles existentes identificados:**

1. token temporário;
2. uso único;
3. resposta genérica quando o e-mail não existe.

**Fragilidade observada:**

O token de recuperação é armazenado em formato utilizável no banco, o que aumenta o impacto caso haja acesso indevido à base.

**Risco residual:** médio para alto.

### 5.3 Cadastro da pessoa monitorada

**Risco principal:** cadastro de titular sem base legal claramente registrada.

**Impacto possível:** tratamento sem comprovação suficiente de consentimento ou outra justificativa formal.

**Controles existentes identificados:**

1. vínculo com usuário autenticado;
2. modelo de dados com campo de consentimento previsto.

**Fragilidade observada:**

O campo de consentimento existe, mas não está sendo preenchido automaticamente na operação atual.

**Risco residual:** alto do ponto de vista de conformidade.

### 5.4 Telemetria e geolocalização

**Risco principal:** exposição de eventos de queda e localização do titular.

**Impacto possível:**

1. violação de privacidade;
2. inferência de rotina;
3. risco à segurança física do titular;
4. estigmatização ou uso indevido de informação sobre fragilidade.

**Controles existentes identificados:**

1. consulta condicionada ao vínculo do responsável autenticado;
2. separação entre entidades de usuário, pessoa monitorada e pulseira.

**Fragilidades observadas:**

1. ausência de política formal de retenção para telemetria;
2. dado de GPS armazenado como string, sem classificação operacional adicional;
3. ausência visível de minimização por granularidade ou descarte programado.

**Risco residual:** alto.

### 5.5 Logs e rastreabilidade

**Risco principal:** logs conterem dado pessoal excessivo ou serem expostos sem necessidade.

**Impacto possível:** vazamento secundário por trilha de auditoria.

**Controles existentes identificados:**

1. existência de trilha de auditoria;
2. estrutura própria para registrar ações críticas.

**Fragilidades observadas:**

1. descrições de log incluem e-mail em alguns casos;
2. endpoint `/logs-auditoria` aparenta estar acessível sem autenticação;
3. ausência visível de retenção e restrição formal de consulta.

**Risco residual:** alto.

## 6. Matriz resumida de risco

| Tratamento | Probabilidade | Impacto | Nível de risco |
|---|---|---|---|
| acesso indevido à conta do responsável | média | alto | alto |
| vazamento de token de recuperação | média | alto | alto |
| ausência de prova de consentimento do monitorado | alta | alto | alto |
| exposição de eventos e geolocalização | média | muito alto | muito alto |
| exposição de logs com dados pessoais | média | alto | alto |
| retenção excessiva de telemetria | alta | médio/alto | alto |

## 7. Medidas técnicas e organizacionais já existentes

O projeto já demonstra várias medidas positivas:

1. autenticação por senha forte;
2. hash de senha com Argon2id;
3. autenticação em dois fatores;
4. bloqueio temporário por tentativas falhas;
5. revogação de JWT em logout;
6. armazenamento seguro de token no app por `flutter_secure_storage`;
7. segregação básica entre usuário, pessoa monitorada, pulseira e evento;
8. existência de log de auditoria.

## 8. Lacunas e impactos identificados

### 8.1 Lacunas técnicas

1. segredo TOTP aparentemente armazenado sem criptografia efetiva no código analisado;
2. token de recuperação armazenado de forma reutilizável no banco;
3. endpoint de logs sem proteção explícita;
4. CORS aberto para qualquer origem no backend;
5. ausência de rotina automática de retenção e descarte.

### 8.2 Lacunas de governança

1. consentimento da pessoa monitorada não registrado no fluxo atual;
2. ausência de política formal de retenção implementada;
3. ausência de classificação formal de criticidade da telemetria;
4. ausência de evidência no código de procedimento para atender direitos do titular além da exclusão de conta do responsável.

## 9. Medidas recomendadas para redução de risco

### Prioridade alta

1. proteger o endpoint `/logs-auditoria` com autenticação e autorização administrativa;
2. implementar registro real do consentimento da pessoa monitorada, com data/hora e origem;
3. criptografar ou proteger adequadamente o segredo TOTP antes da persistência;
4. substituir o armazenamento do token de recuperação por hash do token;
5. definir e implementar política de retenção para telemetria, logs e tokens.

### Prioridade média

1. revisar CORS para produção com lista controlada de origens;
2. reduzir dados pessoais dentro da descrição textual dos logs;
3. documentar bases legais por operação;
4. prever processo para atendimento de direitos do titular monitorado.

### Prioridade estrutural

1. classificar telemetria e GPS como dados de alto impacto;
2. revisar necessidade e granularidade da coleta de localização;
3. formalizar perfis de acesso administrativos e operacionais.

## 10. Avaliação de necessidade e proporcionalidade

Do ponto de vista funcional, o sistema trata dados coerentes com sua finalidade principal: autenticar responsáveis, vincular dispositivos e registrar eventos de monitoramento. Isso indica aderência inicial ao princípio da necessidade.

Por outro lado, a proporcionalidade ainda depende de quatro evoluções importantes:

1. prova efetiva de consentimento ou outra base legal aplicável para o monitorado;
2. retenção limitada da telemetria;
3. endurecimento dos pontos de segurança acessórios;
4. melhor governança sobre logs e dados de localização.

## 11. Conclusão do RIPD

O FallSense possui finalidade legítima e socialmente relevante, com potencial claro de proteção à vida e apoio ao cuidado. Isso fortalece a justificativa do tratamento. Ainda assim, o projeto lida com dados de alto impacto prático, principalmente por envolver monitoramento de pessoa vulnerável e geolocalização.

Com base no estado atual do código, o risco global do tratamento deve ser considerado **alto**, porém **mitigável**. O sistema já possui fundamentos técnicos importantes, mas precisa amadurecer em consentimento, retenção, endurecimento de segredos, proteção de logs e revisão de exposição operacional antes de ser tratado como plenamente aderente a um cenário produtivo mais sensível.
