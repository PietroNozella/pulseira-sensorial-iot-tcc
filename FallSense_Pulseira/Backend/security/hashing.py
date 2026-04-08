from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Configuração central do Argon2id usada para gerar e validar hashes de senha.
# O algoritmo já cria um salt aleatório por conta própria e embute esse valor,
# junto dos parâmetros, na string final armazenada no banco.
ph = PasswordHasher(
    time_cost=3,          # Quantas rodadas de processamento serão aplicadas.
    memory_cost=65536,    # Quantidade de memória usada no cálculo do hash.
    parallelism=4,        # Número de trilhas paralelas usadas pelo algoritmo.
    hash_len=32,          # Tamanho final do hash gerado.
    salt_len=16           # Tamanho do salt aleatório criado para cada senha.
)


# Converte a senha em texto puro para um hash seguro antes da persistência.
def gerar_hash(senha_plana: str) -> str:
    return ph.hash(senha_plana)

# Compara a senha informada no login com o hash salvo no banco.
# O Argon2 recupera automaticamente da própria string o salt e os parâmetros
# usados na geração original.
def verificar_senha(senha_hash_banco: str, senha_tentativa: str) -> bool:
    try:
        # Se a combinação estiver correta, a biblioteca retorna True.
        return ph.verify(senha_hash_banco, senha_tentativa)
    except VerifyMismatchError:
        # Quando a senha não corresponde ao hash armazenado, tratamos a exceção
        # e devolvemos False para o fluxo de autenticação.
        return False
