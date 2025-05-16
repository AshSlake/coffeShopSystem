from tkinter import messagebox


def verificar_preco(preco) -> float:
    """
    Verifica se o preço é valido

    return:
        retorna o preço final formatado

    raise:
        Lança um ValueError caso o preco digitado esteja incorreto.
    """
    # 1. Remove espaços em branco no início e no fim
    preco_limpo = preco.strip()
    # 2. Substitui vírgula por ponto para o float() entender
    preco_normalizado = preco_limpo.replace(
        ",", ".", 1
    )  # O '1' garante que só a primeira vírgula seja trocada (útil se alguém digitar "1,000,00")

    if not preco_normalizado:  # Verifica se, após limpar, a string ficou vazia
        messagebox.showerror("Erro", "O campo preço não pode estar vazio.")
        return

    preco_final = float(preco_normalizado)

    if preco_final < 0:
        messagebox.showerror("Erro", "O preço não pode ser negativo.")
        raise ValueError("O preço não pode ser negativo.")

    return preco_final
