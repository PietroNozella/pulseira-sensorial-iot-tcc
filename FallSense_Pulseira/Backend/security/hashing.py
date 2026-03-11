#Implementar a função que recebe a senha em texto claro e devolve o Hash
#O Argon2 gera o Salt sozinho e o embute na mesma string final

# 1 - Time Cost (Iterações)
# 2 - Memory Cost (Uso de RAM)
# 3 - Parallelism (Uso de threads do processador)

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=3,          # Custo de Tempo (Iterações)
    memory_cost=65536,    # Custo de Memória (64 MB alocados em KB)
    parallelism=4,        # Grau de Paralelismo (Número de threads)
    hash_len=32,          # Tamanho do hash gerado (32 bytes)
    salt_len=16           # Tamanho do salt criptográfico aleatório (16 bytes)
)


# Gerar um hash criptográfico seguro usando Argon2id.
# O 'argon2-cffi' cria automaticamente um Salt único e seguro e o embute na string final retornada   
def gerar_hash(senha_plana: str) -> str:
    return ph.hash(senha_plana)

# Verifica se a senha em texto claro corresponde ao hash do banco de dados
# O Argon2 extrai o salt e os parâmetros da própria string do hash para validar
def verificar_senha(senha_hash_banco: str, senha_tentativa: str) -> bool:
    try:
        # Tenta validar a senha
        return ph.verify(senha_hash_banco, senha_tentativa)
    except VerifyMismatchError:
        # Se as senhas não baterem, a biblioteca levanta essa exceção
        return False
