import os
from cryptography.fernet import Fernet

# --- CHAVE DE EMERGÊNCIA (A mesma que você gerou no terminal) ---
CHAVE = "DWrtRH8v6b3VmIHwhzbeHnYVjEIuMEZdMU0iF6AA0Qo="
fernet = Fernet(CHAVE.encode())

def proteger_dado(texto_limpo: str) -> str:
    return fernet.encrypt(texto_limpo.encode()).decode()

def abrir_dado(texto_criptografado: str) -> str:
    return fernet.decrypt(texto_criptografado.encode()).decode()

# --- SIMULAÇÃO ---
dado_original = "Batimento: 85bpm | Segredo 2FA: JBSW3"

print("--- TESTE DE SEGURANÇA (AES-256) ---")
print(f"1. Dado Original (Texto Limpo): {dado_original}")

try:
    # Criptografando
    dado_protegido = proteger_dado(dado_original)
    print(f"2. Como o dado fica no Supabase (Criptografado): {dado_protegido}")

    # Descriptografando
    dado_recuperado = abrir_dado(dado_protegido)
    print(f"3. Dado recuperado pelo Backend: {dado_recuperado}")

    if dado_original == dado_recuperado:
        print("\n✅ SUCESSO: Criptografia validada para o TCC!")
    else:
        print("\n❌ ERRO: Falha na integridade dos dados.")
except Exception as e:
    print(f"\n💥 ERRO TÉCNICO: {e}")