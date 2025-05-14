import re


def validar_telefone_celular(numero: str) -> bool:
    """
    Valida um número de telefone celular brasileiro.

    Args:
        numero (str): Número de telefone a ser validado (com ou sem formatação)

    Returns:
        bool: True se o número é válido, False caso contrário

    Exemplos válidos:
        (11) 91234-5678
        11912345678
        11 912345678
        912345678
        9 1234 5678
    """
    # Remove todos os caracteres não numéricos
    numero_limpo = re.sub(r"[^0-9]", "", numero)

    # Verifica se tem o tamanho correto (DDD + 9 dígitos ou apenas 9 dígitos)
    if len(numero_limpo) not in (9, 11):
        return False

    # Verifica se o nono dígito é 9 (para números com DDD)
    if len(numero_limpo) == 11 and numero_limpo[2] != "9":
        return False

    # Verifica se o primeiro dígito é 9 (para números sem DDD)
    if len(numero_limpo) == 9 and numero_limpo[0] != "9":
        return False

    # Verifica se todos os dígitos são iguais (não é um número válido)
    if all(d == numero_limpo[0] for d in numero_limpo):
        return False

    return True


# Função de formatação opcional
def formatar_telefone(numero: str) -> str:
    """Formata um número de telefone para o padrão (XX) 9XXXX-XXXX"""
    numero_limpo = re.sub(r"[^0-9]", "", numero)
    if len(numero_limpo) == 11:
        return f"({numero_limpo[:2]}) {numero_limpo[2:7]}-{numero_limpo[7:]}"
    elif len(numero_limpo) == 9:
        return f"{numero_limpo[:1]} {numero_limpo[1:5]} {numero_limpo[5:]}"
    return numero
