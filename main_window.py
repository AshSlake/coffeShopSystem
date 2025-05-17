from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

import mysql, mysql.connector
from src.models.customer import Customers
from src.models.dishes import Dishes
from src.models.login import Login as LoginModel
from src.models.menu import Menu
from src.models.orders import Orders
from src.ui.cardapio_page import CardapioPage
from src.ui.cliente_page import ClientPage
from src.ui.login_page import LoginPage
from src.ui.colaboradores_page import ColaboradoresPage
from src.database.connectFromDB import Database as db
from src.models.phones import Phones
from src.models.address import Address
from src.models.collaborator import Collaborator
from src.ui.pedido_page import PedidoPage
from src.ui.pratos_page import PratosPage
from src.utils.verificadorCpf import validar_cpf
from src.utils.verificadorEndereco import validar_endereco
from src.utils.verificadorPreco import verificar_preco
from src.utils.verificarTelefone import formatar_telefone, validar_telefone_celular


class Main:
    def __init__(
        self, root, titulo: str = "CoffeeShop System", dimensao: str = "1000x650"
    ):
        self.root = root
        self.root.title(titulo)
        self.root.geometry(dimensao)

        largura, altura = 1000, 650
        # backgroud image
        imagem_backgroud = Image.open("src/public/coffeshop.jpg").convert("RGBA")
        # Redimensiona a imagem para o tamanho da janela
        imagem_backgroud = imagem_backgroud.resize(
            (largura, altura), Image.Resampling.LANCZOS
        )
        alpha = int(255 * 0.3)
        # criando mascara
        imagem_backgroud.putalpha(alpha)
        self._bg_photo = ImageTk.PhotoImage(imagem_backgroud)

        self._definir_cores_e_fontes()
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self._configurar_estilos()

        self.container = ttk.Frame(root, style="Background.TFrame")
        self.container.pack(fill="both", expand=True)

        # Estado da aplicação
        self.usuario_logado = False
        self.dados_usuario_logado = None
        self._id_colaborador_editando = None

        # Models
        self.login_model = LoginModel()
        self.db = db()
        self.telefone = Phones(self.db)
        self.endereco = Address(self.db)
        self.colaborador = Collaborator()
        self.cliente = Customers(self.db, self.telefone)
        self.dishes = Dishes(self.db)
        self.menu = Menu(self.db)
        self.order = Orders(self.db)

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
        # View para Clientes
        self.client_page = ClientPage(
            container=self.container,
            limpar_container=self.limpar_container,
            main_controller=self,  # Passa a instância de Main
            cor_fundo_janela=self.cor_fundo_janela,
        )
        # View para Pratos
        self.prato_page = PratosPage(
            container=self.container,
            limpar_container=self.limpar_container,
            main_controller=self,  # Passa a instância de Main
            cor_fundo_janela=self.cor_fundo_janela,
        )
        # View para Cardapio
        self.cardapio_page = CardapioPage(
            container=self.container,
            limpar_container=self.limpar_container,
            main_controller=self,  # Passa a instância de Main
            cor_fundo_janela=self.cor_fundo_janela,
        )
        # View Pedidos
        self.orderPage = PedidoPage(
            container=self.container,
            limpar_container=self.limpar_container,
            main_controller=self,  # Passa a instância de Main
            cor_fundo_janela=self.cor_fundo_janela,
        )

        # Carregar datas
        self.colaboradores_data = None
        self.cliente_data = None
        self.pratos_data = None
        self.pratos_pedido_data = None
        self.cardapio_data = None
        self.pedidos_data = None
        self.reload_data()

        # Iniciar com a tela de login
        self.mostrar_tela("login")

    def reload_data(self):
        """
        Recarrega todas as datas para sempre ficar com os dados atualizados

        """
        self.colaboradores_data = self.colaborador.recuperar_colaboradores_completos()
        self.cliente_data = self.cliente.recuperar_clientes_completos()
        self.pratos_data = self.dishes.recuperar_pratos_completos()
        self.cardapio_data = self.menu.recuperar_cardapio_completo()
        self.pedidos_data = self.order.recuperar_pedidos()

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
        self.style.configure("Bold.TLabel", font=("Helvetica", 10, "bold"))
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
        # Menu Login
        menu_login = tk.Menu(
            barra_menu,
            tearoff=0,
            bg=self.cor_fundo_frame,
            fg=self.cor_texto_escuro,
            font=self.fonte_label,
        )
        menu_login.add_command(label="Sair", command=self.acao_sair)
        barra_menu.add_cascade(label="Login", menu=menu_login)
        # Menu Colaborador
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
        # Menu Cliente
        menu_cliente = tk.Menu(
            barra_menu,
            tearoff=0,
            bg=self.cor_fundo_frame,
            fg=self.cor_texto_escuro,
            font=self.fonte_label,
        )
        menu_cliente.add_command(
            label="Cadastrar Novo Cliente",
            command=lambda: self.mostrar_tela("form_cliente", modo="novo"),
        )
        menu_cliente.add_command(
            label="Clientes",
            command=lambda: self.mostrar_tela("lista_clientes"),
        )
        barra_menu.add_cascade(label="Clientes", menu=menu_cliente)
        # Menu Prato
        menu_pratos = tk.Menu(
            barra_menu,
            tearoff=0,
            bg=self.cor_fundo_frame,
            fg=self.cor_texto_escuro,
            font=self.fonte_label,
        )
        menu_pratos.add_command(
            label="Cadastrar Novo Prato",
            command=lambda: self.mostrar_tela("form_prato", modo="novo"),
        )
        menu_pratos.add_command(
            label="Pratos",
            command=lambda: self.mostrar_tela("lista_pratos"),
        )
        barra_menu.add_cascade(label="Pratos", menu=menu_pratos)
        # Menu Cardapio:
        menu_cardapio = tk.Menu(
            barra_menu,
            tearoff=0,
            bg=self.cor_fundo_frame,
            fg=self.cor_texto_escuro,
            font=self.fonte_label,
        )
        menu_cardapio.add_command(
            label="Mostrar Cardapio",
            command=lambda: self.mostrar_tela("mostrar_cardapio"),
        )
        barra_menu.add_cascade(label="Cardapio", menu=menu_cardapio)
        # Pedidos:
        menu_pedidos = tk.Menu(
            barra_menu,
            tearoff=0,
            bg=self.cor_fundo_frame,
            fg=self.cor_texto_escuro,
            font=self.fonte_label,
        )
        menu_pedidos.add_command(
            label="Mostrar Pedidos",
            command=lambda: self.mostrar_tela("lista_pedidos"),
        )
        barra_menu.add_cascade(label="Pedidos", menu=menu_pedidos)

    # Reseta todos os dados do usuario atual e desliga o menu
    def acao_sair(self):
        self.root.config(menu="")
        self.usuario_logado = False
        self.dados_usuario_logado = None
        self.colaboradores_data = []
        self.mostrar_tela("login")

    def limpar_container(self):
        # destrói tudo
        for widget in self.container.winfo_children():
            widget.destroy()
        # redesenha o background
        bg_label = tk.Label(self.container, image=self._bg_photo)
        bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        # mantém uma referência para não ser coletado pelo garbage collector
        bg_label.image = self._bg_photo

    def mostrar_tela(self, nome_tela, modo="visualizar", data_extra=None):
        self.limpar_container()
        self.reload_data()
        if nome_tela == "form_colaborador":
            # 'data_extra' aqui seria os dados do colaborador para edição
            self.colaboradores_page.criar_form_colaborador(modo, data_extra)
        elif nome_tela == "lista_colaboradores":
            # Passa a lista de dados atual para a página de colaboradores
            self.colaboradores_page.criar_lista_colaboradores(self.colaboradores_data)

            # login
        elif nome_tela == "login":
            self.login_page.criar_tela_login()

            # cliente
        elif nome_tela == "form_cliente":
            self.client_page.criar_form_clientes(modo, data_extra)
        elif nome_tela == "lista_clientes":
            self.client_page.criar_lista_clientes(self.cliente_data)

            # pratos
        elif nome_tela == "form_prato":
            self.prato_page.criar_form_pratos(modo, data_extra)
        elif nome_tela == "lista_pratos":
            self.prato_page.criar_lista_pratos(self.pratos_data)

            # cardapio
        elif nome_tela == "mostrar_cardapio":
            self.cardapio_page.criar_lista_cardapio(self.cardapio_data)

            # Pedidos
        elif nome_tela == "lista_pedidos":
            self.orderPage.criar_lista_pedidos(pedidos_data=self.pedidos_data)
        elif nome_tela == "form_pedido":
            self.orderPage.criar_form_pedido(
                modo="novo",
                data_pratos=self.pratos_data,
                id_colaborador=self._id_colaborador_editando,
            )

            # Tela inicial
        elif nome_tela == "tela_inicial":
            nome_pessoa = self.dados_usuario_logado["pessoa"]["nome"]
            self.mostrar_tela_inicial_conteudo(nome_pessoa)
        else:
            self.login_page.criar_tela_login()

    def mostrar_tela_inicial_conteudo(self, nome_pessoa: str):
        # Este método é chamado por mostrar_tela, não precisa limpar_container
        ttk.Label(
            self.container,
            text=f"Bem-vindo, {nome_pessoa} ao Sistema CoffeeShop",
            style="Welcome.TLabel",
        ).pack(pady=250, padx=20)

    # --- Métodos de Controle de Login ---
    def tentar_login(self, cpf, senha):
        """Valida o login e atualiza a UI."""
        dados_usuario = self.login_model.searchDataFromPerson(cpf, colaborador=True)
        # print(dados_usuario)
        if not dados_usuario or not dados_usuario.get("pessoa"):
            messagebox.showerror("Erro de Login", "CPF ou senha inválidos.")
            return

        self.usuario_logado = True
        self.dados_usuario_logado = dados_usuario

        self._id_colaborador_editando = self.dados_usuario_logado["pessoa"]["cpf"]

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

        # Verificar função
        if not funcao:
            messagebox.showerror("❌Erro", "FUNÇÂO OBRIGATORIA")
            return

        # Verificar nivel sistema
        if not nivelSystem:
            messagebox.showerror("❌Erro", "NIVEL OBRIGATORIO")
            return

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
        self.recarregarListaColaboradores()

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

            self.recarregarListaColaboradores()

    # --- Métodos de Controle de Cliente ---
    def solicitar_edicao_cliente(self, cpf):
        """Prepara e mostra o formulário para editar um cliente."""

        # 1) Puxe sempre os dados completos (com telefone_info)
        self.cliente_data = self.cliente.recuperar_clientes_completos()
        # print(self.cliente_data)

        # 2) Normalize o CPF para string, sem formatação
        cpf_str = "".join(filter(str.isdigit, str(cpf)))

        # 3) Procure convertendo também o que está em cliente_data para string
        cliente = next(
            (
                c
                for c in self.cliente_data
                if "".join(filter(str.isdigit, str(c["cpf"]))) == cpf_str
            ),
            None,
        )

        if not cliente:
            messagebox.showerror("Erro", "Cliente não encontrado para edição.")
            return

        # 4) Passe pro form apenas as chaves que ele vai preencher
        data_para_form = {
            "cpf": cliente["cpf"],
            "nome": cliente["nome"],
            "telefone": cliente.get("telefone_info", ""),
        }

        self.client_page.criar_form_clientes(
            modo="editar", data_colaborador=data_para_form
        )

    def solicitar_exclusao_cliente(self, client_id, nome_cliente):
        """Exclui um cliente após confirmação."""
        if messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir '{nome_cliente}' (CPF: {client_id})?",
        ):
            try:
                self.cliente.deletarCliente(cpf=client_id)
                messagebox.showinfo("Sucesso", "Cliente excluído!")
            except mysql.connector.Error as e:
                print(f"❌erro ao deletar colaborador")
                return

            self.recarregarListaCliente()

    def salvar_dados_cliente(self, dados_cliente, modo: str):
        if not dados_cliente.get("cpf") or not dados_cliente.get("nome"):
            messagebox.showerror("Erro", "CPF e Nome são obrigatórios.")
            return

        cpf = dados_cliente["cpf"]
        nome = dados_cliente["nome"]
        telefone = dados_cliente["telefone"]

        # verificar cpf valido
        if not validar_cpf(cpf):
            messagebox.showerror("❌Erro", "CPF INVÁLIDO")
            return

        # verificar se cpf ja está cadastrado
        if self.cliente.cpf_existe_cliente(cpf) and modo == "novo":
            messagebox.showerror("❌Erro", "CPF JÀ EXISTE")
            return

        # verificar numero de telefone
        if not validar_telefone_celular(telefone):
            messagebox.showerror("❌Erro", "TELEFONE INVALIDO")
            return

        # formata o telefone após verificado
        formated_telefone = formatar_telefone(telefone)

        if modo == "novo":
            self.cliente.inserirCliente(
                cpf=cpf,
                nome=nome,
                telefone=formated_telefone,
            )
        else:
            self.cliente.atualizarCliente(
                cpf=cpf,
                novo_nome=nome,
                novo_telefone=formated_telefone,
            )

        self.recarregarListaCliente()

    def recarregarListaColaboradores(self):
        """metodo para recarregar a lista de colaboradores"""
        self.colaboradores_data = self.colaborador.recuperar_colaboradores_completos()
        self.colaboradores_page.criar_lista_colaboradores(
            colaboradores_data=self.colaboradores_data
        )

    def recarregarListaCliente(self):
        """metodo para recarregar a lista de colaboradores"""
        self.cliente_data = self.cliente.recuperar_clientes_completos()
        self.client_page.criar_lista_clientes(clientes_data=self.cliente_data)

    # --- Métodos de Controle dos Pratos ---

    def recuperar_ingredientes(self) -> list:
        """
        Retorna lista de ingredientes disponíveis para seleção.
        """
        try:
            return self.dishes.recuperar_ingredientes()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao recuperar ingredientes: {e}")
            return []

    def recarregarListaPratos(self):
        """Recarrega dados e atualiza a lista de pratos."""
        self.pratos_data = self.dishes.recuperar_pratos_completos()
        self.prato_page.criar_lista_pratos(self.pratos_data)

    def solicitar_edicao_prato(self, prato_id):
        """Mostra o formulário preenchido para edição de um prato."""
        prato = next((p for p in self.pratos_data if p["id"] == prato_id), None)
        # print(prato)
        if not prato:
            messagebox.showerror("Erro", "Prato não encontrado.")
            return
        data_form = {
            "id": prato["id"],
            "nome": prato["nome"],
            "preco": prato["preco"],
            "ingredientes": prato.get("ingredientes", ""),
        }
        self.prato_page.criar_form_pratos(modo="editar", data_prato=data_form)

    def solicitar_exclusao_prato(self, prato_id):
        """Exclui um prato após confirmação."""
        if messagebox.askyesno("Confirmar Exclusão", f"Excluir prato ID {prato_id}?"):
            success = self.dishes.deletarPrato(prato_id)
            if success:
                messagebox.showinfo("Sucesso", "Prato excluído.")
                self.recarregarListaPratos()

    def salvar_dados_prato(self, dados_prato, modo: str):
        """Salva ou atualiza um prato e suas associações de ingredientes."""
        prato_id = dados_prato.get("id")
        nome = dados_prato.get("nome")
        preco = dados_prato.get("preco")
        ingredientes = dados_prato.get("ingredientes", [])

        if not nome or not preco or not ingredientes:
            messagebox.showerror(
                "Erro", "Todos os campos e ingredientes são obrigatórios."
            )
            return

        # Verificar se o preço é válido
        preco = verificar_preco(preco)

        if modo == "novo":
            prato_id = self.dishes.inserirPrato(nome, float(preco))
            for ing_id in ingredientes:
                self.dishes.adicionarIngredienteAoPrato(prato_id, ing_id)
        else:
            # atualiza dados do prato
            self.dishes.atualizarPrato(
                id_prato=prato_id, novo_nome=nome, novo_preco=float(preco)
            )
            # atualiza ingredientes: remove todos e reinsere
            for ing_id in ingredientes:
                self.dishes.removerIngredienteDoPrato(prato_id, ing_id)
                self.dishes.adicionarIngredienteAoPrato(prato_id, ing_id)
        self.recarregarListaPratos()

    # --- Método de controle do Cardapio ---
    def recarregar_pratos_cardapio(self):
        self.reload_data()
        data = self.cardapio_data
        self.cardapio_page.criar_lista_cardapio(data)

    def adicionar_prato_ao_cardapio(self):
        """Controlador para adiionar pratos ao cardapio"""
        # Faz um filtro dos pratos que não estão no cardapio
        self.reload_data()
        cardapio_id = self.cardapio_data["id"]
        data = [
            prato
            for prato in self.pratos_data
            if prato["id"] not in {p["id"] for p in self.cardapio_data["pratos"]}
        ]

        self.cardapio_page.criar_view_add_Pratos(
            cardapio_id=cardapio_id, data_pratos=data
        )

    def salvar_prato_cardapio(self, cardapio_id: int, selected_ids: dict):
        """
        Controlador para Salvar novos pratos ao cardapio principal.

        args:
            selected_ids(dict): dicionario com as chaves dos pratos para inserção
        """
        pratos = selected_ids.get("pratos", [])
        if not selected_ids:
            messagebox.showerror("Erro", "selecione algum prato.")
            return

        for prato_id in pratos:
            self.menu.adicionarPratoAoCardapio(cardapio_id, prato_id)

        self.recarregar_pratos_cardapio()

    def remover_prato_do_cardapio(self, cardapio_id: int, prato_id: int):
        """
        Controlador para exclusão de um prato do cardapio

        args:
            prato_id(int): chave do prato a ser exluido do cardapio
        """
        self.menu.removerPratoDoCardapio(cardapio_id, prato_id)

    # --- Métodos de controle dos Pedidos ---
    def recarregarListaPedidos(self):
        """Controlador para recarregarar a lista de Pedidos"""
        self.mostrar_tela(nome_tela="lista_pedidos")

    def criar_pedido(self, data_pedidos: dict):
        """
        Controlador para salvar pedidos novos no banco de dados.
        """
        # Recuperar dados para inserção
        num_mesa = data_pedidos["numero_mesa"]
        fk_colaborador = data_pedidos["id_colaborador"]
        status = data_pedidos["status"]
        ids_pratos = data_pedidos["pratos"]

        # Tratamento dos dados

        # validar numero da mesa
        if not num_mesa.isdigit():
            messagebox.showerror("Erro", "Número da mesa inválido!")
            return

        # Validar status
        if not status:
            # Por padrão o status inicial é pendente
            status = "pendente"

        self.order.inserirPedido(num_mesa, fk_colaborador, status, ids_pratos)

    def solicitar_exclusao_pedido(self, pedido_id):
        """
        Controlador de exclusão dos pedidos do banco de dados.
        """
        self.order.deletarPedido(pedido_id)
        self.recarregarListaPedidos()

    def solicitar_edicao_pedido(self, pedido_id):
        """Mostra o formulário preenchido para edição de um pedido."""
        pedido_id = int(pedido_id)
        pedido = self.pedidos_data.get(pedido_id)
        pratos_data = self.dishes.recuperar_pratos_para_pedido(pedido_id)

        if not pratos_data or not pratos_data.get("pratos"):
            messagebox.showerror(
                "Erro", "Pedido não encontrado ou sem pratos disponíveis."
            )
            return

        self.orderPage.criar_form_pedido(
            modo="editar",
            data_pedido=pedido,
            data_pratos=pratos_data["pratos"],
            id_colaborador=self._id_colaborador_editando,
            pedido_id=pedido_id,
        )

    def atualizar_pedido(self, id_pedido, new_data_pedidos):
        """
        Controlador para atualizar um pedido no banco de dados
        """
        novo_num_mesa = new_data_pedidos["numero_mesa"]
        novo_status = new_data_pedidos["status"]
        novos_pratos = new_data_pedidos["pratos"]

        self.order.atualizarPedido(
            id_pedido,
            novo_num_mesa=novo_num_mesa,
            novo_status=novo_status,
            novos_pratos=novos_pratos,
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    root.mainloop()
