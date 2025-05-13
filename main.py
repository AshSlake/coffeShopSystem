import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry


class Main:
    def __init__(
        self, root, titulo: str = "CoffeeShop System", dimensao: str = "1000x650"
    ):
        self.root = root
        self.root.title(titulo)
        self.root.geometry(dimensao)
        # Impede o redimensionamento inicial (opcional, pode remover)
        # self.root.resizable(False, False)

        # --- Paleta de Cores e Fontes ---
        self.cor_fundo_janela = "#F5F5DC"  # Bege (como papel pardo claro)
        self.cor_fundo_frame = "#EADDCA"  # Bege um pouco mais escuro
        self.cor_principal = "#6F4E37"  # Marrom Café
        self.cor_destaque = "#A0522D"  # Marrom Sienna (para botões/hover)
        self.cor_texto_claro = "#FFFFFF"  # Branco
        self.cor_texto_escuro = "#3B2F2F"  # Marrom bem escuro (quase preto)

        self.fonte_titulo = ("Times New Roman", 24, "bold")
        self.fonte_subtitulo = ("Georgia", 16, "bold")
        self.fonte_label = ("Segoe UI", 11)
        self.fonte_entry = ("Segoe UI", 10)
        self.fonte_botao = ("Segoe UI", 10, "bold")
        self.fonte_tree = ("Segoe UI", 10)
        self.fonte_tree_heading = ("Segoe UI", 11, "bold")

        # --- Configuração de Estilo ---
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")

        # Estilo Geral
        self.root.config(bg=self.cor_fundo_janela)
        self.style.configure(
            ".",
            background=self.cor_fundo_frame,
            foreground=self.cor_texto_escuro,
            font=self.fonte_label,
        )

        # Estilo Frames
        self.style.configure("TFrame", background=self.cor_fundo_frame)
        self.style.configure(
            "Background.TFrame", background=self.cor_fundo_janela
        )  # Frame que ocupa tudo

        # Estilo Labels
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
        )  # Para tela inicial

        # Estilo Entry
        self.style.configure(
            "TEntry",
            font=self.fonte_entry,
            fieldbackground="#F5F5F5",  # Fundo do campo de texto
            foreground=self.cor_texto_escuro,
            insertcolor=self.cor_texto_escuro,
        )  # Cor do cursor

        # Estilo Do Botão
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
            background=[("active", self.cor_destaque)],  # Cor ao pressionar/hover
            foreground=[("active", self.cor_texto_claro)],
        )

        # Estilo Treeview
        self.style.configure(
            "Treeview",
            background="#FFFFFF",
            fieldbackground="#FFFFFF",  # Fundo das células
            foreground=self.cor_texto_escuro,
            font=self.fonte_tree,
            rowheight=25,
        )  # Altura da linha
        self.style.configure(
            "Treeview.Heading",
            font=self.fonte_tree_heading,
            background=self.cor_principal,
            foreground=self.cor_texto_claro,
            padding=5,
        )
        self.style.map(
            "Treeview.Heading", background=[("active", self.cor_destaque)]
        )  # Cor ao clicar no cabeçalho

        # --- Estrutura Principal ---
        self.colaboradores = []  # INICIALIZAR A LISTA!
        self.id_colaborador_editando = None  # Para controlar edição

        # Container principal para alternar as telas
        self.container = ttk.Frame(root, style="Background.TFrame")
        self.container.pack(fill="both", expand=True)

        self.criar_menu()
        self.mostrar_tela_inicial()
        # self.carregar_dados_iniciais() # -> Chamar aqui se tiver persistência

    def criar_menu(self):
        barra_menu = tk.Menu(
            self.root,
            bg=self.cor_fundo_janela,
            fg=self.cor_texto_escuro,
            font=self.fonte_label,
        )
        self.root.config(menu=barra_menu)

        # Menu Login
        menu_Login = tk.Menu(
            barra_menu,
            tearoff=0,
            bg=self.cor_fundo_frame,
            fg=self.cor_texto_escuro,
            font=self.fonte_label,
        )
        menu_Login.add_command(
            label="Login", command=lambda: self.mostrar_tela("login")
        )

        menu_Login.add_command(label="Sair", command=lambda: self.mostrar_tela("sair"))
        barra_menu.add_cascade(label="Login", menu=menu_Login)

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
            label="Cadastrar Cliente",
            command=lambda: self.mostrar_tela("form_cliente", modo="novo"),
        )

        menu_cliente.add_command(
            label="Clientes Cadastrados",
            command=lambda: self.mostrar_tela("lista_clientes"),
        )

        barra_menu.add_cascade(label="Clientes", menu=menu_cliente)

        # Menu Pratos
        menu_pratos = tk.Menu(
            barra_menu,
            tearoff=0,
            bg=self.cor_fundo_frame,
            fg=self.cor_texto_escuro,
            font=self.fonte_label,
        )
        menu_pratos.add_command(
            label="Cadastrar Prato",
            command=lambda: self.mostrar_tela("form_prato", modo="novo"),
        )

        menu_pratos.add_command(
            label="Lista dos Pratos",
            command=lambda: self.mostrar_tela("lista_pratos"),
        )

        barra_menu.add_cascade(label="Pratos", menu=menu_pratos)

        # Menu Cardapio
        menu_cardapio = tk.Menu(
            barra_menu,
            tearoff=0,
            bg=self.cor_fundo_frame,
            fg=self.cor_texto_escuro,
            font=self.fonte_label,
        )
        menu_cardapio.add_command(
            label="Cadastrar Cardapio",
            command=lambda: self.mostrar_tela("form_cardapio", modo="novo"),
        )

        menu_cardapio.add_command(
            label="Listar Cardapio",
            command=lambda: self.mostrar_tela("listar_cardapio"),
        )

        barra_menu.add_cascade(label="Cardapio Digital", menu=menu_cardapio)

        # Menu Pedidos
        menu_pedidos = tk.Menu(
            barra_menu,
            tearoff=0,
            bg=self.cor_fundo_frame,
            fg=self.cor_texto_escuro,
            font=self.fonte_label,
        )
        menu_pedidos.add_command(
            label="Inserir Pedidos",
            command=lambda: self.mostrar_tela("form_pedido", modo="novo"),
        )

        menu_pedidos.add_command(
            label="Listar pedidos",
            command=lambda: self.mostrar_tela("listar_pedidos"),
        )

        barra_menu.add_cascade(label="Cardapio Digital", menu=menu_pedidos)

    def limpar_container(self):
        """Remove todos os widgets do container principal."""
        for widget in self.container.winfo_children():
            widget.destroy()

    def mostrar_tela(self, nome_tela, modo="visualizar", data=None):
        """Gerencia as telas do sistema.
        modo: 'novo', 'editar', 'visualizar'
        data: dados a serem carregados na tela (ex: para edição)
        """
        self.limpar_container()
        self.id_colaborador_editando = None  # Reseta o ID de edição ao mudar de tela

        if nome_tela == "form_colaborador":
            self.criar_form_colaborador(modo, data)
        elif nome_tela == "lista_colaboradores":
            self.criar_lista_colaboradores()
        elif nome_tela == "tela_inicial":
            self.mostrar_tela_inicial()
        # Adicionar outras telas aqui...
        else:
            self.mostrar_tela_inicial()  # Padrão

    def mostrar_tela_inicial(self):
        self.limpar_container()
        ttk.Label(
            self.container,
            text="Bem-vindo ao Sistema CoffeeShop",
            style="Welcome.TLabel",
        ).pack(pady=150, padx=20)

    def criar_form_colaborador(self, modo="novo", data=None):
        """Formulário de cadastro/edição de colaborador."""
        self.limpar_container()

        # Frame principal do formulário (centralizado)
        outer_frame = ttk.Frame(self.container, style="Background.TFrame")
        outer_frame.pack(expand=True)  # Para centralizar o frame interno

        frame = ttk.Frame(outer_frame, padding=(30, 20), style="TFrame")
        frame.grid(row=0, column=0)  # Não expande, fica centralizado

        titulo_form = (
            "Cadastrar Novo Colaborador" if modo == "novo" else "Editar Colaborador"
        )
        ttk.Label(frame, text=titulo_form, style="Subtitle.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 25), sticky="w"
        )

        # --- Campos do formulário ---
        labels = [
            "CPF:",
            "Nome Completo:",
            "Telefone:",
            "Endereço:",
            "Data Admissão:",
            "Nível Sistema:",
            "Cargo:",
        ]
        self.entries = {}  # Dicionário para guardar as entries

        for i, label_text in enumerate(labels):
            ttk.Label(frame, text=label_text).grid(
                row=i + 1, column=0, sticky="w", padx=5, pady=8
            )
            entry = ttk.Entry(frame, width=40, style="TEntry")
            entry.grid(row=i + 1, column=1, sticky="ew", padx=5, pady=8)
            # Guarda a entry para acesso posterior (usando texto do label como chave)
            self.entries[label_text] = entry

        # Renomeando as variáveis de instância para usar o dicionário (se precisar de acesso específico)
        self.cpf_entry = self.entries["CPF:"]
        self.nome_entry = self.entries["Nome Completo:"]
        self.telefone_entry = self.entries["Telefone:"]
        self.endereco_entry = self.entries["Endereço:"]
        self.dataAD_entry = self.entries["Data Admissão:"]
        self.nivelSystem_entry = self.entries["Nível Sistema:"]
        self.cargo_entry = self.entries["Cargo:"]

        # Preencher dados se estiver editando
        if modo == "editar" and data:
            self.id_colaborador_editando = data.get("id")  # Guarda o ID
            self.cpf_entry.insert(0, data.get("cpf", ""))
            self.nome_entry.insert(0, data.get("nome", ""))
            self.telefone_entry.insert(0, data.get("telefone", ""))
            self.endereco_entry.insert(0, data.get("endereco", ""))
            self.dataAD_entry.insert(0, data.get("data_admissao", ""))
            self.nivelSystem_entry.insert(0, data.get("nivel_sistema", ""))
            self.cargo_entry.insert(0, data.get("cargo", ""))

        # --- Botões ---
        btn_frame = ttk.Frame(frame, style="TFrame")
        # Coloca abaixo do último campo (row=len(labels)+1)
        btn_frame.grid(
            row=len(labels) + 1, column=0, columnspan=2, pady=(30, 10), sticky="e"
        )

        ttk.Button(
            btn_frame, text="Salvar", command=self.salvar_colaborador, style="TButton"
        ).pack(side="left", padx=(0, 10))
        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self.mostrar_tela_inicial,
            style="TButton",
        ).pack(side="left")

        # Ajustar o grid do frame interno para que a coluna 1 (dos entries) expanda
        frame.columnconfigure(1, weight=1)

    def criar_lista_colaboradores(self):
        """Lista de colaboradores com opções."""
        self.limpar_container()

        frame = ttk.Frame(self.container, padding=20, style="Background.TFrame")
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Gerenciar Colaboradores",
            style="Subtitle.TLabel",
            background=self.cor_fundo_janela,
        ).pack(pady=(0, 15), anchor="w")

        # --- Frame para Treeview e Scrollbar ---
        tree_frame = ttk.Frame(frame, style="TFrame")
        tree_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        # Treeview (tabela)
        columns = ("id", "nome", "cargo", "telefone")  # Adicionei telefone como exemplo
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style="Treeview",  # Aplica o estilo base
            yscrollcommand=scrollbar.set,  # Vincula scrollbar vertical
        )
        scrollbar.config(command=self.tree.yview)

        self.tree.heading("id", text="ID", anchor="w")
        self.tree.heading("nome", text="Nome", anchor="w")
        self.tree.heading("cargo", text="Cargo", anchor="w")
        self.tree.heading("telefone", text="Telefone", anchor="w")

        # Definir largura das colunas (ajuste conforme necessário)
        self.tree.column("id", width=60, stretch=False, anchor="center")
        self.tree.column("nome", width=300, stretch=True)
        self.tree.column("cargo", width=150, stretch=True)
        self.tree.column("telefone", width=150, stretch=True)

        self.tree.pack(fill="both", expand=True)

        # --- Botões de ação ---
        btn_frame = ttk.Frame(frame, style="Background.TFrame")
        btn_frame.pack(fill="x", pady=(10, 0))  # Preenche horizontalmente

        ttk.Button(
            btn_frame,
            text="Adicionar Novo",
            command=lambda: self.mostrar_tela("form_colaborador", modo="novo"),
            style="TButton",
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame,
            text="Editar Selecionado",
            command=self.editar_colaborador,
            style="TButton",
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame,
            text="Excluir Selecionado",
            command=self.excluir_colaborador,
            style="TButton",
        ).pack(side="left", padx=5)
        # O botão Atualizar agora chama um método que só recarrega os dados da treeview
        ttk.Button(
            btn_frame,
            text="Atualizar Lista",
            command=self.atualizar_lista,
            style="TButton",
        ).pack(side="left", padx=5)

        # Carregar os dados na Treeview
        self.atualizar_lista()  # Chama o método para popular a lista

    def salvar_colaborador(self):
        """Salva um novo colaborador ou atualiza um existente."""
        # Coleta todos os dados do formulário
        dados_colaborador = {
            "cpf": self.cpf_entry.get(),
            "nome": self.nome_entry.get(),
            "telefone": self.telefone_entry.get(),
            "endereco": self.endereco_entry.get(),
            "data_admissao": self.dataAD_entry.get(),
            "nivel_sistema": self.nivelSystem_entry.get(),
            "cargo": self.cargo_entry.get(),
            "id": self.id_colaborador_editando,  # Pode ser None se for novo
        }

        # Validação básica (pelo menos nome e cargo)
        if not dados_colaborador["nome"] or not dados_colaborador["cargo"]:
            messagebox.showerror(
                "Erro de Validação", "Os campos Nome e Cargo são obrigatórios!"
            )
            return

        if self.id_colaborador_editando is not None:
            # --- Modo Edição ---
            # Encontra o colaborador na lista e atualiza
            for i, colab in enumerate(self.colaboradores):
                if colab["id"] == self.id_colaborador_editando:
                    # Mantém o ID original, atualiza o resto
                    self.colaboradores[i] = dados_colaborador
                    break
            messagebox.showinfo("Sucesso", "Colaborador atualizado com sucesso!")
            # self.salvar_dados() # -> Chamar aqui para persistir a alteração

        else:
            # --- Modo Adicionar Novo ---
            # Gera um novo ID simples (em um sistema real, use IDs mais robustos)
            novo_id = max((colab["id"] for colab in self.colaboradores), default=0) + 1
            dados_colaborador["id"] = novo_id
            self.colaboradores.append(dados_colaborador)
            messagebox.showinfo("Sucesso", "Colaborador cadastrado com sucesso!")
            # self.salvar_dados() # -> Chamar aqui para persistir o novo dado

        # Limpa o ID de edição e volta para a lista
        self.id_colaborador_editando = None
        self.mostrar_tela("lista_colaboradores")

    def editar_colaborador(self):
        """Prepara a tela de formulário para edição."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning(
                "Nenhuma Seleção",
                "Por favor, selecione um colaborador na lista para editar.",
            )
            return

        item_id_str = self.tree.item(selected_items[0])["values"][
            0
        ]  # Pega o ID da primeira coluna
        try:
            item_id = int(item_id_str)
        except (ValueError, TypeError):
            messagebox.showerror(
                "Erro", f"ID inválido na linha selecionada: {item_id_str}"
            )
            return

        # Encontrar os dados completos do colaborador na lista self.colaboradores
        colaborador_data = None
        for colab in self.colaboradores:
            if colab.get("id") == item_id:
                colaborador_data = colab
                break

        if colaborador_data:
            # Passa os dados para a função que cria o formulário no modo 'editar'
            self.mostrar_tela("form_colaborador", modo="editar", data=colaborador_data)
        else:
            messagebox.showerror(
                "Erro",
                f"Não foi possível encontrar os dados do colaborador com ID {item_id}.",
            )

    def excluir_colaborador(self):
        """Exclui o colaborador selecionado."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning(
                "Nenhuma Seleção",
                "Por favor, selecione um colaborador na lista para excluir.",
            )
            return

        item_values = self.tree.item(selected_items[0])["values"]
        item_id_str = item_values[0]
        nome_colaborador = item_values[1]  # Pega o nome para a mensagem

        try:
            item_id = int(item_id_str)
        except (ValueError, TypeError):
            messagebox.showerror(
                "Erro", f"ID inválido na linha selecionada: {item_id_str}"
            )
            return

        if messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o colaborador '{nome_colaborador}' (ID: {item_id})?",
        ):
            # Remove da lista de dados principal
            self.colaboradores = [
                colab for colab in self.colaboradores if colab.get("id") != item_id
            ]
            # Remove da Treeview
            self.tree.delete(selected_items[0])
            messagebox.showinfo("Sucesso", "Colaborador excluído com sucesso!")
            # self.salvar_dados() # -> Chamar aqui para persistir a exclusão

    def atualizar_lista(self):
        """Limpa e recarrega os dados na Treeview."""
        # Verifica se a Treeview já foi criada
        if hasattr(self, "tree"):
            # Limpa todos os itens existentes na Treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Repopula a Treeview com os dados atuais de self.colaboradores
            # Adapte as colunas aqui conforme a ordem em 'columns' e os dados em self.colaboradores
            for colab in self.colaboradores:
                # Use .get() para evitar erros se alguma chave faltar no dicionário
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        colab.get("id", ""),
                        colab.get("nome", ""),
                        colab.get("cargo", ""),
                        colab.get("telefone", ""),  # Exemplo com telefone
                        # Adicione mais colunas conforme necessário
                    ),
                )
        # else:
        # Se a treeview não existe, talvez chamar a criação da tela?
        # self.mostrar_tela("lista_colaboradores")
        # Mas geralmente é chamado depois da criação.


if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    root.mainloop()
