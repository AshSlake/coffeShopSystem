def validar_cpf(cpf):
    """
    Valida um CPF verificando seu formato e dígitos verificadores.

    Args:
        cpf: String contendo o CPF (com ou sem pontuação)

    Returns:
        bool: True se o CPF é válido, False caso contrário
    """

    # Remove caracteres não numéricos
    cpf = "".join(filter(str.isdigit, cpf))

    # Verifica se tem 11 dígitos ou se é uma sequência de dígitos repetidos
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    # Verifica se os dígitos calculados conferem com os informados
    return int(cpf[9]) == digito1 and int(cpf[10]) == digito2
