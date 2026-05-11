# Registro das Operações de Tratamento de Dados Pessoais

## 1. Objetivo

Este documento registra, de forma organizada, as principais operações de tratamento de dados pessoais realizadas pelo projeto FallSense. Ele funciona como um ROPA, ou seja, um inventário operacional de como os dados entram, circulam, são usados, armazenados e eventualmente eliminados.

## 2. Contexto do sistema

O FallSense é um sistema de monitoramento voltado à detecção de quedas, composto por:

1. aplicativo móvel para o responsável;
2. backend em FastAPI;
3. banco PostgreSQL/Supabase;
4. pulseira IoT vinculada à pessoa monitorada;
5. integração com Brevo para envio de e-mails.

## 3. Papéis no tratamento

### 3.1 Controlador

Para fins documentais, o controlador tende a ser a organização, equipe ou projeto responsável por definir por que e como os dados são tratados.

No contexto acadêmico deste repositório, isso normalmente corresponde ao próprio projeto FallSense e seus responsáveis institucionais.

### 3.2 Operadores

Com base na arquitetura identificada:

| Agente | Papel provável |
|---|---|
| Supabase/PostgreSQL | operador de armazenamento |
| Brevo | operador de comunicação por e-mail |
| infraestrutura de hospedagem da API | operador de processamento/infraestrutura |

Esse enquadramento precisa ser validado conforme o ambiente real de implantação.

## 4. Registro das operações

### Operação 1. Cadastro de usuário responsável

| Item | Descrição |
|---|---|
| Finalidade | criar conta de acesso ao sistema |
| Titular | usuário responsável/cuidador |
| Dados tratados | nome completo, e-mail, telefone, senha |
| Forma de coleta | formulário de cadastro |
| Base legal sugerida | execução do serviço e procedimentos preliminares |
| Compartilhamento | banco de dados |
| Retenção | enquanto a conta permanecer ativa, salvo obrigação diversa |
| Medidas de segurança | hash de senha com Argon2id, validação de senha forte |

**Explicação didática:**  
Essa operação é a porta de entrada do sistema. Sem ela, o usuário não consegue criar uma conta para acompanhar a pessoa monitorada. O sistema coleta apenas os dados necessários para identificar o responsável e permitir autenticação.

### Operação 2. Geração e gestão de autenticação em dois fatores

| Item | Descrição |
|---|---|
| Finalidade | reforçar a segurança da conta |
| Titular | usuário responsável |
| Dados tratados | segredo TOTP, códigos de recuperação, challenge temporário de login |
| Forma de coleta | geração automática pelo backend |
| Base legal sugerida | legítimo interesse em segurança e proteção da conta |
| Compartilhamento | banco de dados e retorno controlado ao usuário no registro |
| Retenção | enquanto o mecanismo 2FA estiver ativo |
| Medidas de segurança | TOTP, códigos de recuperação com hash, limitação de tentativas |

**Explicação didática:**  
Aqui o sistema não depende só da senha. Ele cria um segundo fator para dificultar invasões. É um tratamento voltado à segurança e não à finalidade principal de monitoramento.

### Operação 3. Login e gestão de sessão

| Item | Descrição |
|---|---|
| Finalidade | autenticar o usuário e permitir uso da aplicação |
| Titular | usuário responsável |
| Dados tratados | e-mail, senha, código 2FA, token JWT, contador de falhas, bloqueio temporário |
| Forma de coleta | formulário de login e processamento interno |
| Base legal sugerida | execução do serviço e segurança |
| Compartilhamento | app móvel e banco de dados em parte do fluxo |
| Retenção | token com validade temporária; registros acessórios conforme política interna |
| Medidas de segurança | JWT com expiração, revogação em logout, lockout por tentativas falhas |

**Explicação didática:**  
Essa operação garante que só usuários autorizados acessem os dados da pessoa monitorada. É uma operação central porque protege todas as demais.

### Operação 4. Recuperação de senha

| Item | Descrição |
|---|---|
| Finalidade | restabelecer acesso do usuário |
| Titular | usuário responsável |
| Dados tratados | e-mail, token de recuperação, nova senha |
| Forma de coleta | solicitação pelo app e envio por e-mail |
| Base legal sugerida | execução do serviço e segurança da conta |
| Compartilhamento | Brevo e banco de dados |
| Retenção | token temporário de curta duração |
| Medidas de segurança | expiração, uso único, resposta genérica para evitar enumeração |

**Explicação didática:**  
Quando o usuário esquece a senha, o sistema trata dados mínimos para devolver o acesso. Como existe comunicação por e-mail, essa operação já envolve compartilhamento com terceiro operador.

### Operação 5. Consulta e atualização de perfil

| Item | Descrição |
|---|---|
| Finalidade | manter dados cadastrais corretos |
| Titular | usuário responsável |
| Dados tratados | nome completo, e-mail, telefone |
| Forma de coleta | tela de perfil |
| Base legal sugerida | execução do serviço |
| Compartilhamento | banco de dados |
| Retenção | enquanto a conta existir |
| Medidas de segurança | autenticação obrigatória, log de auditoria |

**Explicação didática:**  
Essa operação permite correção e atualização de dados. Pela LGPD, isso é importante porque se conecta ao princípio da qualidade dos dados.

### Operação 6. Cadastro da pessoa monitorada

| Item | Descrição |
|---|---|
| Finalidade | identificar a pessoa assistida pela pulseira |
| Titular | pessoa monitorada |
| Dados tratados | nome completo; campo previsto para data de consentimento |
| Forma de coleta | cadastro feito pelo responsável autenticado |
| Base legal sugerida | consentimento ou proteção da vida, a depender do cenário |
| Compartilhamento | banco de dados |
| Retenção | enquanto durar a relação de monitoramento |
| Medidas de segurança | acesso restrito ao usuário autenticado vinculado |

**Explicação didática:**  
Essa é a primeira operação diretamente ligada ao titular monitorado. Por isso, merece atenção especial quanto à legitimidade do cadastro e ao registro do consentimento.

### Operação 7. Vinculação da pulseira ao titular monitorado

| Item | Descrição |
|---|---|
| Finalidade | associar o dispositivo físico à pessoa monitorada |
| Titular | pessoa monitorada e usuário responsável vinculado |
| Dados tratados | MAC address, versão de firmware, vínculo com pessoa monitorada |
| Forma de coleta | cadastro manual ou integração |
| Base legal sugerida | execução do serviço |
| Compartilhamento | banco de dados |
| Retenção | enquanto a pulseira estiver vinculada ao monitoramento |
| Medidas de segurança | autenticação do responsável e validação de vínculo |

**Explicação didática:**  
O MAC address parece técnico, mas passa a ser um dado pessoal indireto quando identifica o dispositivo usado por uma pessoa específica.

### Operação 8. Registro de telemetria e eventos de queda

| Item | Descrição |
|---|---|
| Finalidade | detectar, registrar e consultar eventos relevantes da pulseira |
| Titular | pessoa monitorada |
| Dados tratados | MAC address, tipo de evento, coordenadas GPS, data/hora |
| Forma de coleta | backend após evento associado à pulseira |
| Base legal sugerida | proteção da vida e da incolumidade física; eventualmente consentimento complementar |
| Compartilhamento | banco de dados e consulta pelo responsável autenticado |
| Retenção | precisa de política formal específica |
| Medidas de segurança | autenticação por vínculo com o responsável, histórico limitado a consultas recentes na API |

**Explicação didática:**  
Essa é a operação mais sensível do projeto. Ela revela rotina, localização e eventos físicos potencialmente críticos do titular monitorado.

### Operação 9. Geração de logs de auditoria

| Item | Descrição |
|---|---|
| Finalidade | rastrear ações críticas e apoiar segurança |
| Titular | principalmente o usuário responsável |
| Dados tratados | usuário vinculado, ação, descrição, data/hora, status |
| Forma de coleta | geração automática pelo backend |
| Base legal sugerida | legítimo interesse, segurança e prevenção a fraudes |
| Compartilhamento | banco de dados; endpoint interno de consulta |
| Retenção | não formalizada tecnicamente no código |
| Medidas de segurança | trilha de auditoria centralizada |

**Explicação didática:**  
Logs ajudam muito na segurança, mas também podem virar fonte adicional de exposição. Por isso, precisam de controle de acesso e política de retenção.

### Operação 10. Exclusão de conta

| Item | Descrição |
|---|---|
| Finalidade | encerrar a relação do usuário com o serviço |
| Titular | usuário responsável e, indiretamente, pessoa monitorada vinculada |
| Dados tratados | dados da conta, vínculos com pessoa monitorada e pulseira |
| Forma de coleta | solicitação autenticada com senha |
| Base legal sugerida | exercício de direito do titular e término da relação |
| Compartilhamento | banco de dados |
| Retenção | exclusão lógica/física conforme implementação |
| Medidas de segurança | confirmação por senha, revogação de token |

**Explicação didática:**  
Essa operação é importante para o princípio da necessidade. O sistema já possui fluxo de exclusão, o que é positivo do ponto de vista de governança.

## 5. Fluxo resumido entre sistemas

1. O app coleta dados do usuário responsável.
2. O backend valida, autentica e grava dados no PostgreSQL/Supabase.
3. A pulseira e os eventos são vinculados à pessoa monitorada.
4. Em recuperação de senha, o backend compartilha e-mail e conteúdo do envio com a Brevo.
5. O app armazena localmente o token JWT em armazenamento seguro do dispositivo.

## 6. Riscos operacionais percebidos no registro

Os seguintes pontos merecem constar no ROPA como observações:

1. O consentimento da pessoa monitorada está previsto no modelo de dados, mas não aparece implementado no fluxo de cadastro.
2. O endpoint de logs de auditoria aparenta estar sem proteção de autenticação.
3. O armazenamento do segredo TOTP e do token de recuperação merece reforço técnico.
4. Não foi identificado mecanismo automático de descarte de telemetria e logs antigos.

## 7. Conclusão

O registro das operações mostra que o FallSense possui um fluxo de tratamento relativamente bem delimitado e tecnicamente compreensível. O sistema tem operações compatíveis com o objetivo do projeto, mas por lidar com monitoramento de pessoa potencialmente vulnerável, precisa de formalização mais forte em consentimento, retenção, controle de acesso e proteção de dados de autenticação e telemetria.
