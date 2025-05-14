from tkinter import messagebox, ttk


class ClientPage:
    def __init__(
        self,
        container,
        limpar_container,
        main_controller,  # Instância da classe Main
        cor_fundo_janela,
    ):
        # Dependências externas
        self.container = container
        self.limpar_container = limpar_container
        self.main_controller = main_controller
        self.cor_fundo_janela = cor_fundo_janela
        self.data_admissao_entry = None

        # Estado interno da UI (para o formulário)
        self._id_colaborador_editando_form = None
        self.entries = {}
        self.tree = None
        self.nivel_sistema_combobox = None
        self.cargo_combobox = None

    def criar_form_clientes(self, modo="novo", data_colaborador=None):
        self.limpar_container()
        self._id_colaborador_editando_form = None

        outer_frame = ttk.Frame(self.container, style="Background.TFrame")
        outer_frame.pack(expand=True)

        frame = ttk.Frame(outer_frame, padding=(30, 20), style="TFrame")
        frame.grid(row=0, column=0)

        titulo_form = "Cadastrar Novo Cliente" if modo == "novo" else "Editar Cliente"
        ttk.Label(frame, text=titulo_form, style="Subtitle.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 25), sticky="w"
        )

        labels_fields = [
            ("CPF:", "cpf", "Entry"),
            ("Nome Completo:", "nome", "Entry"),
            ("Telefone:", "telefone", "Entry"),
        ]
        self.entries = {}  # Dicionário para guardar as entries e o DateEntry

        for i, field_info in enumerate(labels_fields):
            label_text, field_key, widget_type = (
                field_info[0],
                field_info[1],
                field_info[2],
            )
            ttk.Label(frame, text=label_text).grid(
                row=i + 1, column=0, sticky="w", padx=5, pady=8
            )
            entry_widget = None
            entry_widget = ttk.Entry(frame, width=40, style="TEntry")

            entry_widget.grid(row=i + 1, column=1, sticky="ew", padx=5, pady=8)
            self.entries[field_key] = entry_widget

        # Preencher dados se estiver editando
        if modo == "editar" and data_colaborador:

            self.entries["cpf"].insert(0, data_colaborador.get("cpf", ""))
            self.entries["nome"].insert(0, data_colaborador.get("nome", ""))
            self.entries["telefone"].insert(0, data_colaborador.get("telefone", ""))

        btn_frame = ttk.Frame(frame, style="TFrame")
        btn_frame.grid(
            row=len(labels_fields) + 1,
            column=0,
            columnspan=2,
            pady=(30, 10),
            sticky="e",
        )

        ttk.Button(
            btn_frame,
            text="Salvar",
            command=lambda: self._handle_salvar_cliente(modo),
            style="TButton",
        ).pack(side="left", padx=(0, 10))
        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self._handle_cancelar_form_cliente,
            style="TButton",
        ).pack(side="left")

        frame.columnconfigure(1, weight=1)

    def _handle_salvar_cliente(self, modo):

        # Coleta todos os dados do formulário
        dados_cliente = {
            "cpf": self.entries["cpf"].get(),
            "nome": self.entries["nome"].get(),
            "telefone": self.entries["telefone"].get(),
        }
        self.main_controller.salvar_dados_cliente(dados_cliente, modo)

    def criar_lista_clientes(self, clientes_data):
        """Cria a lista de clientes recuperando dados do MySQL"""

        self.limpar_container()

        frame = ttk.Frame(self.container, padding=20, style="Background.TFrame")
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Gerenciar Clientes",
            style="Subtitle.TLabel",
            background=self.cor_fundo_janela,
        ).pack(pady=(0, 15), anchor="w")

        tree_frame = ttk.Frame(frame, style="TFrame")
        tree_frame.pack(fill="both", expand=True, pady=(0, 15))

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        columns = (
            "cpf",
            "nome",
            "telefone",
        )
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style="Treeview",
            yscrollcommand=scrollbar.set,
        )
        scrollbar.config(command=self.tree.yview)

        # Configura os cabeçalhos
        self.tree.heading("cpf", text="CPF", anchor="w")
        self.tree.heading("nome", text="Nome", anchor="w")
        self.tree.heading("telefone", text="Telefone", anchor="w")

        # Configura as colunas
        self.tree.column("cpf", width=120, stretch=False)
        self.tree.column("nome", width=200, stretch=True)
        self.tree.column("telefone", width=120, stretch=False)

        self.tree.pack(fill="both", expand=True)

        # Preenche a treeview com os dados
        for colab in clientes_data:

            self.tree.insert(
                "",
                "end",
                values=(
                    colab["cpf"],
                    colab["nome"],
                    colab["telefone_info"],
                ),
            )

        btn_frame = ttk.Frame(frame, style="Background.TFrame")
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Adicionar Novo",
            command=lambda: self.main_controller.mostrar_tela(
                "form_cliente", modo="novo"
            ),
            style="TButton",
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Editar Selecionado",
            command=self._handle_editar_selecionado,
            style="TButton",
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Excluir Selecionado",
            command=self._handle_excluir_selecionado,
            style="TButton",
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Atualizar Lista",
            command=self._handle_atualizar_lista_cliente,  # Agora recarrega os dados diretamente
            style="TButton",
        ).pack(side="left", padx=5)

    def _handle_cancelar_form_cliente(self):
        """Notifica o controller principal para voltar à tela de lista ou inicial."""
        # Por padrão, volta para a lista de clientes.
        self.main_controller.mostrar_tela("lista_clientes")

    def _handle_atualizar_lista_cliente(self):
        """chama o metodo para recarregar a lista de clientes."""
        self.main_controller.recarregarListaCliente()

    def _handle_editar_selecionado(self):
        """Solicita ao controller principal para mostrar o formulário de edição."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning(
                "Nenhuma Seleção", "Selecione um cliente para editar."
            )
            return
        item_id_str = self.tree.item(selected_items[0])["values"][0]
        try:
            item_id = int(item_id_str)
            self.main_controller.solicitar_edicao_cliente(item_id)
        except (ValueError, TypeError):
            messagebox.showerror("Erro", f"CPF inválido: {item_id_str}")

    def _handle_excluir_selecionado(self):
        """Solicita ao controller principal para excluir um colaborador."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning(
                "Nenhuma Seleção", "Selecione um colaborador para excluir."
            )
            return

        item_values = self.tree.item(selected_items[0])["values"]
        item_id_str = item_values[0]
        nome_cliente = item_values[1]
        try:
            item_id = item_id_str
            self.main_controller.solicitar_exclusao_cliente(item_id, nome_cliente)
        except (ValueError, TypeError):
            messagebox.showerror("Erro", f"CPF inválido: {item_id_str}")
