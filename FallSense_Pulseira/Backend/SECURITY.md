# Documentação de Segurança — FallSense Backend

## 1. Hash de Senhas com Argon2id

### Algoritmo escolhido

O projeto utiliza **Argon2id**, vencedor da Password Hashing Competition (PHC) em 2015 e recomendado pelo OWASP como primeira escolha para hash de senhas em 2024. A variante `id` combina resistência a ataques de canal lateral (característica do Argon2i) com resistência a ataques de GPU e ASIC (característica do Argon2d), sendo a opção mais equilibrada para autenticação de usuários.

### Parâmetros configurados e justificativas

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| `time_cost` | 3 | Número de iterações sobre a memória. O mínimo recomendado pelo OWASP é 1; 3 iterações aumentam o custo computacional por fator de ~3x sem impacto perceptível ao usuário (< 1 segundo em hardware comum). |
| `memory_cost` | 65536 KB (64 MB) | Quantidade de RAM alocada por operação de hash. Valores altos inviabilizam ataques em paralelo com GPU, pois cada tentativa exige memória dedicada. O OWASP recomenda mínimo de 19 MB; 64 MB oferece margem de segurança adequada para o perfil do projeto. |
| `parallelism` | 4 | Número de threads utilizadas. Ajustado ao hardware de servidor típico (4 núcleos), maximizando o custo para o atacante sem sobrecarregar o servidor legítimo. |
| `hash_len` | 32 bytes | Tamanho do hash resultante (256 bits). Suficiente para resistir a colisões com ampla margem de segurança. |
| `salt_len` | 16 bytes | Tamanho do salt criptográfico gerado automaticamente (128 bits). O OWASP recomenda mínimo de 16 bytes. O salt é único por hash e embutido na string final pelo próprio Argon2. |

### Salt

O salt é gerado automaticamente pela biblioteca `argon2-cffi` usando o gerador criptograficamente seguro do sistema operacional (`os.urandom`). Ele é **único por hash** e armazenado embutido na string resultante, junto com os parâmetros utilizados — eliminando a necessidade de coluna separada no banco de dados.

---

## 2. Fluxo de Autenticação

### 2.1 Registro

```
Cliente                     API                        Banco
  |                           |                           |
  |-- POST /auth/registrar --> |                           |
  |   { email, senha, ... }   |                           |
  |                           |-- verifica e-mail único ->|
  |                           |<-- e-mail disponível -----|
  |                           |                           |
  |                           | gerar_hash(senha)         |
  |                           | gerar_segredo_totp()      |
  |                           | _gerar_recovery_codes()   |
  |                           |                           |
  |                           |-- INSERT usuarios_api --->|
  |                           |<-- commit OK -------------|
  |                           |                           |
  |<-- 201 { totp_secret,     |                           |
  |    recovery_codes } ------|                           |
```

- A senha nunca é armazenada em texto plano — apenas o hash Argon2id.
- O `totp_secret` e os `recovery_codes` são retornados **uma única vez** no registro. Não há endpoint para recuperá-los posteriormente.

### 2.2 Login (dois fatores)

```
Cliente                     API                        Banco
  |                           |                           |
  |-- POST /auth/login ------> |                           |
  |   { email, senha }        |                           |
  |                           |-- busca usuário por e-mail|
  |                           |                           |
  |                           | verifica lockout_until    |
  |                           | (bloqueio por força bruta)|
  |                           |                           |
  |                           | verificar_senha(hash, senha)
  |                           | [falha] failed_attempts++ |
  |                           | [>= 3 falhas] lockout 5min|
  |                           |                           |
  |<-- { requer_2fa: true } --|                           |
  |                           |                           |
  |-- POST /auth/login ------> |                           |
  |   { email, senha,         |                           |
  |     codigo_2fa }          |                           |
  |                           | verificar_totp(secret, codigo)
  |                           | [falha] failed_attempts++ |
  |                           |                           |
  |                           | reseta failed_attempts    |
  |                           | criar_token_jwt(email)    |
  |                           |                           |
  |<-- { access_token } ------|                           |
```

- A validação da senha ocorre **antes** do 2FA — o código TOTP só é solicitado após a senha correta.
- O bloqueio por força bruta se aplica tanto a falhas de senha quanto a falhas de TOTP.

### 2.3 Logout e Invalidação de Sessão

```
Cliente                     API                        Banco
  |                           |                           |
  |-- POST /auth/logout -----> |                           |
  |   Authorization: Bearer   |                           |
  |   <token>                 |                           |
  |                           | verificar_token_jwt(token)|
  |                           | (valida assinatura,       |
  |                           |  expiração e blacklist)   |
  |                           |                           |
  |                           |-- INSERT tokens_revogados>|
  |                           |-- INSERT logs_auditoria ->|
  |                           |<-- commit OK -------------|
  |                           |                           |
  |<-- { mensagem: "Logout"} -|                           |
```

- Após o logout, o token é inserido na tabela `tokens_revogados`. Qualquer requisição subsequente com o mesmo token é rejeitada com HTTP 401.

### 2.4 Recuperação de Senha

```
Cliente                     API                        Banco / E-mail
  |                           |                           |
  |-- POST /auth/esqueci-senha|                           |
  |   { email }               |                           |
  |                           |-- busca usuário ---------->|
  |                           | secrets.token_urlsafe(32) |
  |                           | expiracao = agora + 15min |
  |                           |-- INSERT tokens_recuperacao
  |                           |-- INSERT logs_auditoria ->|
  |                           |-- envia e-mail ----------->
  |<-- { mensagem: "..." } ---|                           |
  |                           |                           |
  |-- POST /auth/resetar-senha|                           |
  |   { token, nova_senha }   |                           |
  |                           |-- busca token não usado -->|
  |                           | valida expiração          |
  |                           | gerar_hash(nova_senha)    |
  |                           | token.usado = True        |
  |                           |-- INSERT logs_auditoria ->|
  |<-- { mensagem: "Senha ... }                           |
```

- A resposta de `/esqueci-senha` é genérica mesmo quando o e-mail não existe, para não vazar informações sobre usuários cadastrados.
- O token é invalidado imediatamente após o uso — não pode ser reutilizado.

---

## 3. Justificativas das Escolhas de Segurança

### JWT com HS256 (expiração de 60 minutos)

O JSON Web Token é utilizado como mecanismo de sessão stateless. O algoritmo HS256 (HMAC-SHA256) foi escolhido por ser adequado para sistemas onde o mesmo servidor que emite o token também o valida — o caso deste projeto. A chave secreta (`JWT_SECRET`) é carregada obrigatoriamente de variável de ambiente; o servidor recusa inicialização sem ela.

A expiração de 60 minutos equilibra segurança (limita a janela de uso de um token comprometido) e usabilidade (evita logouts involuntários frequentes em sessões normais de uso da pulseira).

Tokens revogados via logout são persistidos na tabela `tokens_revogados`, tornando o mecanismo efetivamente stateful no caso de logout explícito.

### TOTP via pyotp (Google Authenticator)

O segundo fator utiliza o algoritmo TOTP (Time-based One-Time Password, RFC 6238), implementado pela biblioteca `pyotp`. O segredo é gerado com `pyotp.random_base32()` (160 bits de entropia) e armazenado criptografado no banco. O código de 6 dígitos gerado pelo aplicativo autenticador é válido por 30 segundos, o que inviabiliza ataques de replay fora dessa janela.

### Proteção contra Força Bruta

Após 3 tentativas consecutivas de autenticação com falha (senha ou TOTP), a conta é bloqueada por 5 minutos via campo `lockout_until` no banco de dados. O bloqueio é persistente entre requisições e resiste a reinicializações do servidor. O contador é zerado automaticamente após autenticação bem-sucedida.

### Token de Recuperação de Senha

O token é gerado com `secrets.token_urlsafe(32)`, que produz 32 bytes de entropia (equivalente a ~256 bits) codificados em Base64 URL-safe. Isso inviabiliza adivinhação por força bruta. O token expira em 15 minutos e é marcado como `usado=True` imediatamente após o reset — impedindo reutilização mesmo dentro da janela de validade.

### Armazenamento de Credenciais

Todas as credenciais sensíveis (chave JWT, senha de e-mail, URL do banco) são carregadas exclusivamente de variáveis de ambiente via `python-dotenv`. O servidor falha explicitamente na inicialização caso qualquer variável obrigatória esteja ausente, evitando execução com configuração insegura silenciosa.
