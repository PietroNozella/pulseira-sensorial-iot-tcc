# Backlog - Funcionalidades de Perfil

Objetivo: colocar em funcionamento as telas e botoes criados no fluxo de perfil, priorizando menor impacto e entregas incrementais.

## P0 - Editar perfil funcionando

### 1. Criar endpoint para atualizar dados do usuario

Contexto: o app ja consome `GET /auth/me`, mas ainda nao existe endpoint para salvar nome, e-mail ou telefone.

Entrypoints:
- `FallSense_Pulseira/Backend/routers/auth.py`
- `FallSense_Pulseira/Backend/schemas/auth_schemas.py`

Escopo:
- Criar schema de update de perfil.
- Criar rota autenticada, sugestao: `PATCH /auth/me`.
- Permitir atualizar `nome_completo`, `email` e `telefone`.
- Validar conflito de e-mail quando o novo e-mail ja existir em outro usuario.
- Retornar o perfil atualizado no mesmo formato de `PerfilResponse`.

Aceite:
- Usuario autenticado consegue atualizar dados pessoais.
- Token invalido retorna 401.
- E-mail duplicado retorna erro claro.
- `GET /auth/me` retorna os dados atualizados apos salvar.

### 2. Conectar formulario de informacoes pessoais na API

Contexto: `PersonalInfoFormWidget` ja renderiza campos, mas o botao `Salvar Alteracoes` ainda esta com TODO.

Entrypoints:
- `FallSense_Pulseira/Frontend/lib/core/network/api_service.dart`
- `FallSense_Pulseira/Frontend/lib/features/profile/presentation/widgets/personal_info_form_widget.dart`
- `FallSense_Pulseira/Frontend/lib/features/auth/presentation/providers/auth_provider.dart`

Escopo:
- Adicionar metodo `atualizarPerfil` no `ApiService`.
- Buscar token via `StorageService`.
- Validar campos antes de enviar.
- Exibir loading enquanto salva.
- Exibir feedback de sucesso/erro.
- Invalidar/atualizar `userProfileProvider` apos sucesso.
- Atualizar nome salvo localmente quando necessario.

Aceite:
- Botao salva alteracoes reais no backend.
- Header do perfil reflete o novo nome sem precisar relogar.
- Erros da API aparecem de forma compreensivel.
- Botao nao dispara chamadas duplicadas durante loading.

## P0 - Alterar senha funcionando

### 3. Criar endpoint para alterar senha autenticada

Contexto: o backend tem reset de senha por token, mas nao tem troca de senha logada.

Entrypoints:
- `FallSense_Pulseira/Backend/routers/auth.py`
- `FallSense_Pulseira/Backend/schemas/auth_schemas.py`
- `FallSense_Pulseira/Backend/security/hashing.py`

Escopo:
- Criar schema com `senha_atual` e `nova_senha`.
- Criar rota autenticada, sugestao: `PATCH /auth/me/senha`.
- Validar senha atual com `verificar_senha`.
- Reutilizar regra de forca de senha.
- Salvar hash da nova senha.

Aceite:
- Senha atual incorreta retorna erro claro.
- Nova senha fraca e rejeitada.
- Apos atualizar, login com senha antiga falha e login com senha nova funciona.

### 4. Conectar formulario de alterar senha na API

Contexto: `ChangePasswordFormWidget` ja tem campos e controle de visibilidade, mas o botao `Atualizar Senha` ainda esta com TODO.

Entrypoints:
- `FallSense_Pulseira/Frontend/lib/core/network/api_service.dart`
- `FallSense_Pulseira/Frontend/lib/features/profile/presentation/widgets/change_password_form_widget.dart`

Escopo:
- Adicionar metodo `alterarSenha` no `ApiService`.
- Validar campos vazios.
- Validar confirmacao da nova senha antes da chamada.
- Exibir loading, sucesso e erro.
- Limpar campos apos sucesso.

Aceite:
- Usuario consegue alterar senha pela tela.
- Confirmacao divergente bloqueia envio.
- Campos sao limpos apos sucesso.
- Erros de senha atual/API sao exibidos no app.

## P1 - Exclusao de conta funcionando

### 5. Criar endpoint para excluir conta autenticada

Contexto: `DeleteAccountDialogWidget` coleta a senha, mas nao existe chamada real para excluir a conta.

Entrypoints:
- `FallSense_Pulseira/Backend/routers/auth.py`
- `FallSense_Pulseira/Backend/schemas/auth_schemas.py`
- `FallSense_Pulseira/Backend/models/user.py`

Escopo:
- Criar schema com `senha`.
- Criar rota autenticada, sugestao: `DELETE /auth/me`.
- Validar senha antes de excluir.
- Confirmar comportamento de cascata para dados vinculados.
- Revogar token atual ou garantir sessao encerrada apos exclusao.

Aceite:
- Senha incorreta nao exclui conta.
- Senha correta exclui o usuario.
- Token antigo nao permite acessar recursos depois da exclusao.
- Dados dependentes respeitam as regras de FK/cascade existentes.

### 6. Conectar zona de perigo na API

Contexto: `DangerZoneWidget` abre o dialog, mas nao faz chamada de exclusao.

Entrypoints:
- `FallSense_Pulseira/Frontend/lib/core/network/api_service.dart`
- `FallSense_Pulseira/Frontend/lib/features/profile/presentation/widgets/danger_zone_widget.dart`
- `FallSense_Pulseira/Frontend/lib/features/profile/presentation/widgets/delete_account_dialog_widget.dart`
- `FallSense_Pulseira/Frontend/lib/services/storage_service.dart`

Escopo:
- Adicionar metodo `excluirConta` no `ApiService`.
- Exibir loading durante exclusao.
- Exibir erro quando senha for invalida.
- Limpar sessao local apos sucesso.
- Redirecionar para tela inicial/login sem permitir voltar para area autenticada.

Aceite:
- Fluxo completo exclui a conta e desloga o usuario.
- Cancelar dialog nao faz chamada.
- Campo de senha vazio nao permite confirmar exclusao.

## P1 - Remover botoes mortos do perfil

### 7. Dar comportamento inicial aos itens de menu ainda vazios

Contexto: na `ProfileScreen`, estes itens ainda possuem `onTap: () {}`:
- `Contatos de Emergencia`
- `Autenticacao e Seguranca`
- `Permissoes do App`
- `Registro Completo de Eventos`

Entrypoint:
- `FallSense_Pulseira/Frontend/lib/features/profile/presentation/screens/profile_screen.dart`

Escopo:
- Evitar botoes sem resposta.
- Para funcionalidades que ainda nao existem, usar um feedback simples: `Funcionalidade em desenvolvimento`.
- Para `Registro Completo de Eventos`, avaliar reaproveitar dados de `telemetryEventsProvider` em uma tela simples de listagem.

Aceite:
- Nenhum item clicavel fica sem feedback.
- Itens futuros nao prometem uma tela inexistente.
- O usuario entende quando a funcionalidade ainda nao esta disponivel.

## P2 - Qualidade e validacao

### 8. Validar fluxo completo de perfil

Entrypoints:
- `FallSense_Pulseira/Frontend/test`
- Testes manuais no app

Escopo:
- Testar editar perfil.
- Testar alterar senha.
- Testar exclusao de conta.
- Testar erro de token expirado/invalido.
- Testar responsividade basica da tela de perfil.

Aceite:
- Fluxos principais funcionam de ponta a ponta.
- Nao ha botoes sem acao.
- Falhas comuns exibem mensagem clara.
- Nao ha regressao no login/logout.

## Ordem sugerida

1. Card 1
2. Card 2
3. Card 3
4. Card 4
5. Card 7
6. Card 5
7. Card 6
8. Card 8
