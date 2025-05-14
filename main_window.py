from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import mysql, mysql.connector
from src.models.login import Login as LoginModel
from src.ui.login_page import LoginPage
from src.ui.colaboradores_page import ColaboradoresPage
from src.database.connectFromDB import Database as db
from src.models.phones import Phones
from src.models.address import Address
from src.models.collaborator import Collaborator
from src.utils.verificadorCpf import validar_cpf
from src.utils.verificadorEndereco import validar_endereco
from src.utils.verificarTelefone import formatar_telefone, validar_telefone_celular


class Main:
    def __init__(
        self, root, titulo: str = "CoffeeShop System", dimensao: str = "1000x650"
    ):
        self.root = root
        self.root.title(titulo)
        self.root.geometry(dimensao)

        self._definir_cores_e_fontes()
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self._configurar_estilos()

        self.container = ttk.Frame(root, style="Background.TFrame")
        self.container.pack(fill="both", expand=True)

        # Estado da aplicação
        self.usuario_logado = False
        self.dados_usuario_logado = None

        self._id_colaborador_editando = (
            None  # ID do colaborador sendo editado (se houver)
        )

        # Modelos
        self.login_model = LoginModel()

        # Views (Páginas da UI)
        # View Login
        self.login_page = LoginPage(
            container=self.container,
            limpar_container=self.limpar_container,
            main_controller=self,  # Passa a instância de Main
            cor_fundo_janela=self.cor_fundo_janela,
        )
        # View Colaboradores:
        self.colaboradores_page = ColaboradoresPage(
            container=self.container,
            limpar_container=self.limpar_container,
            main_controller=self,  # Passa a instância de Main
            cor_fundo_janela=self.cor_fundo_janela,
        )
        self.db = db()
        self.telefone = Phones(self.db)
        self.endereco = Address(self.db)
        self.colaborador = Collaborator()
        self.colaboradores_data = self.colaborador.recuperar_colaboradores_completos()

        # Iniciar com a tela de login
        self.mostrar_tela("login")

    # Styles:
    def _definir_cores_e_fontes(self):
        self.cor_fundo_janela = "#F5F5DC"
        self.cor_fundo_frame = "#EADDCA"
        self.cor_principal = "#6F4E37"
        self.cor_destaque = "#A0522D"
        self.cor_texto_claro = "#FFFFFF"
        self.cor_texto_escuro = "#3B2F2F"
        self.fonte_titulo = ("Times New Roman", 24, "bold")
        self.fonte_subtitulo = ("Georgia", 16, "bold")
        self.fonte_label = ("Segoe UI", 11)
        self.fonte_entry = ("Segoe UI", 10)
        self.fonte_botao = ("Segoe UI", 10, "bold")
        self.fonte_tree = ("Segoe UI", 10)
        self.fonte_tree_heading = ("Segoe UI", 11, "bold")

    def _configurar_estilos(self):
        self.root.config(bg=self.cor_fundo_janela)
        self.style.configure(
            ".",
            background=self.cor_fundo_frame,
            foreground=self.cor_texto_escuro,
            font=self.fonte_label,
        )
        self.style.configure("TFrame", background=self.cor_fundo_frame)
        self.style.configure("Background.TFrame", background=self.cor_fundo_janela)
        self.style.configure(
            "TLabel", background=self.cor_fundo_frame, font=self.fonte_label
        )
        self.style.configure(
            "Title.TLabel",
            background=self.cor_fundo_frame,
            font=self.fonte_titulo,
            foreground=self.cor_principal,
        )
        self.style.configure(
            "Subtitle.TLabel",
            background=self.cor_fundo_frame,
            font=self.fonte_subtitulo,
            foreground=self.cor_principal,
        )
        self.style.configure(
            "Welcome.TLabel",
            background=self.cor_fundo_janela,
            font=self.fonte_titulo,
            foreground=self.cor_principal,
        )
        self.style.configure(
            "TEntry",
            font=self.fonte_entry,
            fieldbackground="#F5F5F5",
            foreground=self.cor_texto_escuro,
            insertcolor=self.cor_texto_escuro,
        )
        self.style.configure(
            "TButton",
            font=self.fonte_botao,
            padding=8,
            background=self.cor_principal,
            foreground=self.cor_texto_claro,
            borderwidth=0,
        )
        self.style.map(
            "TButton",
            background=[("active", self.cor_destaque)],
            foreground=[("active", self.cor_texto_claro)],
        )
        self.style.configure(
            "Treeview",
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground=self.cor_texto_escuro,
            font=self.fonte_tree,
            rowheight=25,
        )
        self.style.configure(
            "Treeview.Heading",
            font=self.fonte_tree_heading,
            background=self.cor_principal,
            foreground=self.cor_texto_claro,
            padding=5,
        )
        self.style.configure(
            "TCombobox",
            font=self.fonte_entry,  # Usa a mesma fonte do Entry
            fieldbackground="#F5F5F5",
            foreground=self.cor_texto_escuro,
            selectbackground=self.cor_destaque,  # Cor de fundo do item selecionado na lista
            selectforeground=self.cor_texto_claro,  # Cor do texto do item selecionado na lista
        )
        self.style.map("Treeview.Heading", background=[("active", self.cor_destaque)])

    # Criação do Menu:
    def criar_menu(self):
        barra_menu = tk.Menu(
            self.root,
            bg=self.cor_fundo_janela,
            fg=self.cor_texto_escuro,
            font=self.fonte_label,
        )
        self.root.config(menu=barra_menu)
        menu_login = tk.Menu(
            barra_menu,
            tearoff=0,
            bg=self.cor_fundo_frame,
            fg=self.cor_texto_escuro,
            font=self.fonte_label,
        )
        menu_login.add_command(label="Sair", command=self.acao_sair)
        barra_menu.add_cascade(label="Login", menu=menu_login)
        menu_colab = tk.Menu(
            barra_menu,
            tearoff=0,
            bg=self.cor_fundo_frame,
            fg=self.cor_texto_escuro,
            font=self.fonte_label,
        )
        menu_colab.add_command(
            label="Cadastrar Novo Colaborador",
            command=lambda: self.mostrar_tela("form_colaborador", modo="novo"),
        )
        menu_colab.add_command(
            label="Colaboradores",
            command=lambda: self.mostrar_tela("lista_colaboradores"),
        )
        barra_menu.add_cascade(label="Colaboradores", menu=menu_colab)

    # Reseta todos os dados do usuario atual e desliga o menu
    def acao_sair(self):
        self.root.config(menu="")
        self.usuario_logado = False
        self.dados_usuario_logado = None
        self.colaboradores_data = []
        self.mostrar_tela("login")

    def limpar_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def mostrar_tela(self, nome_tela, modo="visualizar", data_extra=None):
        self.limpar_container()
        if nome_tela == "form_colaborador":
            # 'data_extra' aqui seria os dados do colaborador para edição
            self.colaboradores_page.criar_form_colaborador(modo, data_extra)
        elif nome_tela == "lista_colaboradores":
            # Passa a lista de dados atual para a página de colaboradores
            self.colaboradores_page.criar_lista_colaboradores(self.colaboradores_data)
        elif nome_tela == "login":
            self.login_page.criar_tela_login()
        elif nome_tela == "tela_inicial":
            nome_pessoa = self.dados_usuario_logado["pessoa"]["nome"]
            self.mostrar_tela_inicial_conteudo(nome_pessoa)
        else:  # Fallback para tela de login
            self.login_page.criar_tela_login()

    def mostrar_tela_inicial_conteudo(self, nome_pessoa: str):
        # Este método é chamado por mostrar_tela, não precisa limpar_container
        ttk.Label(
            self.container,
            text=f"Bem-vindo, {nome_pessoa} ao Sistema CoffeeShop",
            style="Welcome.TLabel",
        ).pack(pady=150, padx=20)

    # --- Métodos de Controle de Login ---
    def tentar_login(self, cpf, senha):
        """Valida o login e atualiza a UI."""
        dados_usuario = self.login_model.searchDataFromPerson(cpf, colaborador=True)

        if not dados_usuario or not dados_usuario.get("pessoa"):
            messagebox.showerror("Erro de Login", "CPF ou senha inválidos.")
            return

        self.usuario_logado = True
        self.dados_usuario_logado = dados_usuario

        # Após login bem-sucedido:
        self.mostrar_tela("tela_inicial")
        self.criar_menu()

    # --- Métodos de Controle de Colaboradores ---
    def salvar_dados_colaborador(self, dados_colaborador, modo: str):
        """Salva ou atualiza dados de um colaborador."""

        if not dados_colaborador.get("cpf") or not dados_colaborador.get("nome"):
            messagebox.showerror("Erro", "CPF e Nome são obrigatórios.")
            return

        cpf = dados_colaborador["cpf"]
        nome = dados_colaborador["nome"]
        dataAd = dados_colaborador["data_admissao"]
        data_ad_formatada_sql = datetime.strptime(
            dataAd, "%d/%m/%Y"
        )  # Converte a data para inserir no banco
        nivelSystem = dados_colaborador["nivel_sistema"]
        funcao = dados_colaborador["cargo"]
        telefone = dados_colaborador["telefone"]
        endereco = dados_colaborador["endereco"]

        # verificar cpf valido
        if not validar_cpf(cpf):
            messagebox.showerror("❌Erro", "CPF INVÁLIDO")
            return

        # verificar se cpf ja está cadastrado
        if self.colaborador.cpf_existe(cpf) and modo == "novo":
            messagebox.showerror("❌Erro", "CPF JÀ EXISTE")
            return

        # verificar numero de telefone
        if not validar_telefone_celular(telefone):
            messagebox.showerror("❌Erro", "TELEFONE INVALIDO")
            return

        # verificar endereco
        if not validar_endereco(endereco):
            messagebox.showerror("❌Erro", "ENDEREÇO INVALIDO")
            return

        # formata o telefone após verificado
        formated_telefone = formatar_telefone(telefone)

        if modo == "novo":
            self.colaborador.inserirColaborador(
                cpf=cpf,
                nome=nome,
                dataAd=data_ad_formatada_sql,
                nivelSystem=nivelSystem,
                funcao=funcao,
                telefone=formated_telefone,
                endereco=endereco,
            )
        else:
            self.colaborador.atualizarColaborador(
                cpf=cpf,
                novo_nome=nome,
                nova_data_AD=data_ad_formatada_sql,
                novo_nivel_system=nivelSystem,
                nova_funcao=funcao,
                novo_telefone=formated_telefone,
                novo_endereco=endereco,
            )
        self.recarregarLista()

    def solicitar_edicao_colaborador(self, colab_id):
        """Prepara e mostra o formulário para editar um colaborador."""
        colaborador = next(
            (c for c in self.colaboradores_data if c["cpf"] == colab_id), None
        )

        self.colaboradores_page.criar_form_colaborador(
            modo="editar", data_colaborador=colaborador
        )

    def solicitar_exclusao_colaborador(self, colab_id, nome_colaborador):
        """Exclui um colaborador após confirmação."""
        if messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir '{nome_colaborador}' (CPF: {colab_id})?",
        ):
            try:
                self.colaborador.deletarColaborador(cpf_colaborador=colab_id)
                messagebox.showinfo("Sucesso", "Colaborador excluído!")
            except mysql.connector.Error as e:
                print(f"❌erro ao deletar colaborador")
                return

            self.recarregarLista()  # Atualiza a lista

    def recarregarLista(self):
        """metodo para recarregar a lista de colaboradores"""
        self.colaboradores_data = self.colaborador.recuperar_colaboradores_completos()
        self.colaboradores_page.criar_lista_colaboradores(
            colaboradores_data=self.colaboradores_data
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    root.mainloop()
