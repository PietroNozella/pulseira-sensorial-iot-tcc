# Fluxo de Atendimento aos Direitos dos Titulares (LGPD)

## 1. Objetivo
Este documento formaliza como o sistema FallSense operacionaliza o atendimento aos direitos dos titulares de dados pessoais, conforme exigido pelo Artigo 18 da Lei Geral de Proteção de Dados (Lei nº 13.709/2018).

Com base no atual estágio de desenvolvimento do projeto (conforme mapeado no Relatório de Impacto à Proteção de Dados - RIPD), o atendimento é realizado por meio de um modelo híbrido: algumas operações já estão automatizadas na API, enquanto outras dependem de solicitação manual junto à equipe de suporte.

## 2. Direitos Garantidos e Fluxos Atuais

### 2.1. Direito à Correção de Dados Incompletos ou Desatualizados (Art. 18, inciso III)
* **Status:** Automatizado.
* **Fluxo:** O usuário possui autonomia para retificar seus dados cadastrais (nome completo, e-mail e telefone) diretamente pelas configurações do perfil no aplicativo.
* **Mecanismo Técnico:** A API recebe e processa a atualização através do payload validado pelo schema `PerfilUpdatePayload`.

### 2.2. Direito à Eliminação dos Dados (Direito ao Esquecimento - Art. 18, inciso VI)
* **Status:** Automatizado.
* **Fluxo:** O titular pode solicitar o encerramento da sua conta e exclusão dos seus dados a qualquer momento, mediante confirmação da sua senha de acesso para evitar exclusões acidentais ou indevidas.
* **Mecanismo Técnico:** A API processa a exclusão exigindo o schema `ExcluirContaPayload`. Conforme o modelo de dados atual, a exclusão da conta do responsável cessa os vínculos sistêmicos e interrompe a coleta de telemetria.

### 2.3. Direito de Confirmação, Acesso e Portabilidade (Art. 18, incisos I, II e V)
* **Status:** Processo Manual (Em evolução).
* **Fluxo:** Como ainda não há endpoints automatizados para exportação de dados estruturados (JSON) diretamente pelo aplicativo, o titular deve exercer esse direito entrando em contato com a equipe pelo e-mail. A equipe técnica fará a extração dos dados do banco (PostgreSQL/Supabase) e os enviará ao titular em formato legível.
* **Nota de Conformidade:** A criação de rotas específicas para automatizar a portabilidade está listada como uma melhoria no plano de governança e no backlog da arquitetura do sistema.

### 2.4. Direito à Revogação do Consentimento (Art. 18, inciso IX)
* **Status:** Híbrido.
* **Fluxo:** A revogação do consentimento para o monitoramento contínuo pode ser exercida de forma indireta pela exclusão da conta (automatizado) ou mediante solicitação para desvinculação específica do dispositivo (via suporte). O sistema prevê a evolução para que essa desvinculação ocorra de forma isolada via aplicativo no futuro.

## 3. Rastreabilidade Jurídica
Para garantir a prestação de contas (Princípio da Responsabilização - Art. 6º, X), o sistema conta com a tabela centralizada de `logs_auditoria`. Ações críticas, como acesso à conta, alteração de credenciais e exclusão, geram entradas no log contendo:

* O identificador do usuário responsável;
* A ação realizada;
* A descrição técnica do evento;
* O status da requisição (Sucesso/Falha);
* O timestamp automático.

Dessa forma, o projeto FallSense mantém uma trilha de auditoria capaz de provar tecnicamente o cumprimento das ações sistêmicas relacionadas ao tratamento de dados.
