# QA - Fluxo de Perfil do App

Objetivo: validar manualmente o fluxo completo de perfil depois das entregas P0 e P1.

## Pre-condicoes

- Backend publicado/local com as rotas:
  - `GET /auth/me`
  - `PATCH /auth/me`
  - `PATCH /auth/me/senha`
  - `DELETE /auth/me`
- App apontando para a API correta em `FallSense_Pulseira/Frontend/lib/core/network/api_service.dart`.
- Usuario de teste com 2FA configurado.

## 1. Login e acesso ao perfil

Passos:
1. Abrir o app.
2. Fazer login com e-mail, senha e 2FA validos.
3. Acessar a aba `Perfil`.

Aceite:
- Login conclui sem erro.
- Header do perfil exibe o nome do usuario.
- O item `Editar Perfil` abre a tela de edicao.

## 2. Editar informacoes pessoais

Passos:
1. Entrar em `Perfil > Editar Perfil`.
2. Alterar nome e telefone.
3. Tocar em `Salvar Alteracoes`.
4. Voltar para a tela de perfil.

Aceite:
- Botao mostra loading durante a requisicao.
- App exibe mensagem de sucesso.
- Header do perfil reflete o novo nome.
- Ao sair e entrar de novo, os dados atualizados continuam salvos.

Cenarios de erro:
- Nome vazio deve mostrar erro no app.
- E-mail duplicado deve mostrar erro claro vindo da API.
- Token expirado/invalido deve mostrar erro de sessao.

## 3. Alterar senha

Passos:
1. Entrar em `Perfil > Editar Perfil`.
2. Preencher senha atual, nova senha e confirmacao.
3. Tocar em `Atualizar Senha`.
4. Fazer logout.
5. Tentar login com senha antiga.
6. Fazer login com senha nova.

Aceite:
- Senha antiga deixa de funcionar.
- Senha nova funciona.
- Campos de senha sao limpos apos sucesso.
- Confirmacao divergente bloqueia envio.
- Senha atual incorreta mostra erro.
- Senha fraca mostra erro.

## 4. Excluir conta

Passos:
1. Entrar em `Perfil > Editar Perfil`.
2. Tocar em `Excluir minha conta`.
3. Cancelar o dialog.
4. Reabrir o dialog e tentar confirmar com senha vazia.
5. Informar senha incorreta.
6. Informar senha correta.

Aceite:
- Cancelar nao faz chamada destrutiva.
- Senha vazia nao permite confirmar.
- Senha incorreta nao exclui a conta.
- Senha correta exclui a conta, limpa a sessao e volta para login.
- Nao e possivel acessar area autenticada com o token antigo.
- Login com a conta excluida falha.

## 5. Menu de perfil

Passos:
1. Tocar em `Contatos de Emergencia`.
2. Tocar em `Autenticacao e Seguranca`.
3. Tocar em `Permissoes do App`.
4. Tocar em `Registro Completo de Eventos`.

Aceite:
- Nenhum item fica sem resposta.
- Itens ainda nao implementados exibem `Funcionalidade em desenvolvimento.`

## 6. Responsividade basica

Passos:
1. Testar a tela de perfil em celular pequeno.
2. Testar em tela maior/emulador tablet.
3. Abrir teclado nos campos de perfil e senha.

Aceite:
- Conteudo continua rolavel.
- Botoes nao ficam escondidos permanentemente pelo teclado.
- Textos e campos nao se sobrepoem.
- Dialog de exclusao cabe na tela.

## Validacao automatizada executada

Backend:

```bash
python -m pytest
```

Resultado esperado atual:

```text
37 passed
```

Frontend:

```bash
flutter test
flutter analyze
```

Observacao: no ambiente atual do Codex, `flutter` e `dart` nao estao no PATH. Rodar localmente na maquina com Flutter instalado.
