import re


def validar_endereco(endereco: str) -> bool:
    """
    Valida um endereço.
    A validação pode ser ajustada conforme os critérios do sistema, como:
    - O endereço não pode ser vazio
    - O endereço deve ter pelo menos 10 caracteres
    - O endereço não pode conter caracteres especiais inválidos

    exemples:
        "Rua das Flores, 123",  # Válido
        "Av. Paulista, 1500",   # Válido
        "Rua",                  # Inválido (muito curto)
        "Rua !@#%",             # Inválido (caracteres especiais)
        ""                      # Inválido (vazio)
    """

    # Verifica se o endereço está vazio
    if not endereco:
        print("❌ Endereço não pode ser vazio.")
        return False

    # Verifica se o endereço tem pelo menos 10 caracteres (ajustável conforme necessidade)
    if len(endereco) < 10:
        print("❌ Endereço deve ter pelo menos 10 caracteres.")
        return False

    # Verifica se o endereço contém caracteres especiais inválidos
    # Vamos assumir que o endereço pode conter letras, números, espaços, vírgulas e pontos
    if not re.match(r"^[a-zA-Z0-9\s,.-]+$", endereco):
        print("❌ Endereço contém caracteres inválidos.")
        return False

    # Se todas as validações passarem
    print("✅ Endereço válido.")
    return True
