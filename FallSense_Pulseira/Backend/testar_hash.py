# testar_hash.py
from security.hashing import gerar_hash, verificar_senha

print("--- INICIANDO TESTE DO ARGON2ID ---\n")

# 1. O usuário digita a senha no cadastro
senha_secreta = "ProjetoIntegrador@2026"
print(f"1. Senha Original em texto claro: '{senha_secreta}'")

# 2. O sistema gera o hash para salvar no banco de dados
hash_salvo_no_banco = gerar_hash(senha_secreta)
print(f"2. Hash Gerado (Argon2id + Salt): \n   {hash_salvo_no_banco}\n")

# 3. Simulação de Login: Sucesso
print("3. Testando Login com a senha CORRETA...")
sucesso = verificar_senha(hash_salvo_no_banco, "ProjetoIntegrador@2026")
print(f"   Acesso permitido? -> {sucesso}")

# 4. Simulação de Login: Falha (Ataque/Erro de digitação)
print("\n4. Testando Login com a senha ERRADA...")
falha = verificar_senha(hash_salvo_no_banco, "senha_errada_123")
print(f"   Acesso permitido? -> {falha}")