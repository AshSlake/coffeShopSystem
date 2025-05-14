from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import datetime
from src.enums.Enums import Cargos, NivelSistema

OPCOES_CARGO_DISPLAY = [cargo.value for cargo in Cargos]
DESCRICOES_NIVEL = {
    NivelSistema.ADMINISTRADOR: "Acesso total ao sistema",
    NivelSistema.GERENTE: "Gerencia toda a cafeteria",
    NivelSistema.BARISTA_MASTER: "Barista experiente com supervisão",
    NivelSistema.BARISTA: "Prepara bebidas e atende clientes",
    NivelSistema.ATENDENTE: "Atendimento no balcão/caixa",
    NivelSistema.AUXILIAR: "Auxiliar de limpeza e apoio geral",
}
OPCOES_NIVEL_SISTEMA = [
    f"{nivel.value} - {nivel.name.replace('_', ' ').title()} - {DESCRICOES_NIVEL[nivel]}"
    for nivel in NivelSistema
]


class ColaboradoresPage:
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

    def criar_form_colaborador(self, modo="novo", data_colaborador=None):
        self.limpar_container()
        self._id_colaborador_editando_form = None

        outer_frame = ttk.Frame(self.container, style="Background.TFrame")
        outer_frame.pack(expand=True)

        frame = ttk.Frame(outer_frame, padding=(30, 20), style="TFrame")
        frame.grid(row=0, column=0)

        titulo_form = (
            "Cadastrar Novo Colaborador" if modo == "novo" else "Editar Colaborador"
        )
        ttk.Label(frame, text=titulo_form, style="Subtitle.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 25), sticky="w"
        )

        labels_fields = [
            ("CPF:", "cpf", "Entry"),
            ("Nome Completo:", "nome", "Entry"),
            ("Telefone:", "telefone", "Entry"),
            ("Endereço:", "endereco", "Entry"),
            ("Data Admissão:", "data_admissao", "DateEntry"),
            ("Nível Sistema:", "nivel_sistema", "Combobox", OPCOES_NIVEL_SISTEMA),
            ("Cargo:", "cargo", "Combobox", OPCOES_CARGO_DISPLAY),
        ]
        self.entries = {}  # Dicionário para guardar as entries e o DateEntry

        for i, field_info in enumerate(labels_fields):
            label_text, field_key, widget_type = (
                field_info[0],
                field_info[1],
                field_info[2],
            )
            options = field_info[3] if len(field_info) > 3 else None

            ttk.Label(frame, text=label_text).grid(
                row=i + 1, column=0, sticky="w", padx=5, pady=8
            )
            entry_widget = None
            if widget_type == "DateEntry":
                # date_pattern para definir como a data é exibida e obtida
                # 'dd/mm/yyyy' é um formato comum no Brasil
                # locale='pt_BR' para nomes de meses/dias em português no calendário pop-up
                entry_widget = DateEntry(
                    frame,
                    width=38,
                    style="TEntry",
                    date_pattern="dd/mm/yyyy",
                    locale="pt_BR",
                )
                self.data_admissao_entry = entry_widget  # Guarda referência específica
            elif widget_type == "Combobox":
                entry_widget = ttk.Combobox(
                    frame, width=38, values=options, state="readonly", style="TCombobox"
                )
                if field_key == "nivel_sistema":
                    self.nivel_sistema_combobox = entry_widget
                elif field_key == "cargo":
                    self.cargo_combobox = entry_widget
            else:
                entry_widget = ttk.Entry(frame, width=40, style="TEntry")

            entry_widget.grid(row=i + 1, column=1, sticky="ew", padx=5, pady=8)
            self.entries[field_key] = entry_widget

        # Preencher dados se estiver editando
        if modo == "editar" and data_colaborador:
            self._id_colaborador_editando_form = data_colaborador.get("id")
            self.entries["cpf"].insert(0, data_colaborador.get("cpf", ""))
            self.entries["nome"].insert(0, data_colaborador.get("nome", ""))
            self.entries["telefone"].insert(0, data_colaborador.get("telefone", ""))
            self.entries["endereco"].insert(0, data_colaborador.get("endereco", ""))

            # --- Tratamento para Data Admissão ---
            data_ad_str = data_colaborador.get("data_admissao", "")
            if data_ad_str:
                try:
                    # Tenta converter a string da data para um objeto date
                    # Ajuste o formato '%d/%m/%Y' se seu armazenamento usar outro
                    data_obj = datetime.datetime.strptime(
                        data_ad_str, "%d/%m/%Y"
                    ).date()
                    self.data_admissao_entry.set_date(data_obj)
                except ValueError:
                    print(
                        f"Aviso: Data de admissão '{data_ad_str}' não está no formato dd/mm/yyyy."
                    )

            # --- Preencher Comboboxes ---
            nivel_sistema_val = data_colaborador.get("nivel_sistema", "")
            if nivel_sistema_val and self.nivel_sistema_combobox:
                try:
                    nivel = NivelSistema(int(nivel_sistema_val))
                    display_text = f"{nivel.value} - {nivel.name.replace('_', ' ').title()} - {DESCRICOES_NIVEL[nivel]}"
                    self.nivel_sistema_combobox.set(display_text)
                except (ValueError, KeyError):
                    print(
                        f"Aviso: Nível de sistema '{nivel_sistema_val}' não encontrado"
                    )

            cargo_val = data_colaborador.get("cargo", "")
            if cargo_val and self.cargo_combobox:
                if cargo_val in OPCOES_CARGO_DISPLAY:
                    self.cargo_combobox.set(cargo_val)
                else:
                    print(f"Aviso: Cargo '{cargo_val}' não é uma opção válida.")

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
            command=self._handle_salvar_colaborador,
            style="TButton",
        ).pack(side="left", padx=(0, 10))
        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self._handle_cancelar_form,
            style="TButton",
        ).pack(side="left")

        frame.columnconfigure(1, weight=1)

    def _handle_salvar_colaborador(self):
        # Obtém o texto selecionado
        nivel_selecionado = self.nivel_sistema_combobox.get()

        # Extrai o valor numérico (primeira parte antes do hífen)
        nivel_value = None
        if nivel_selecionado:
            try:
                nivel_value = int(nivel_selecionado.split("-")[0].strip())
            except (ValueError, IndexError):
                messagebox.showerror("Erro", "Selecione um nível de sistema válido")
                return

        # Coleta todos os dados do formulário
        dados_colaborador = {
            "cpf": self.entries["cpf"].get(),
            "nome": self.entries["nome"].get(),
            "telefone": self.entries["telefone"].get(),
            "endereco": self.entries["endereco"].get(),
            "data_admissao": (
                self.data_admissao_entry.get_date().strftime("%d/%m/%Y")
                if self.data_admissao_entry.get_date()
                else ""
            ),
            "nivel_sistema": nivel_value,
            "cargo": self.cargo_combobox.get() if self.cargo_combobox else "",
            "id": self._id_colaborador_editando_form,
        }
        self.main_controller.salvar_dados_colaborador(dados_colaborador)

    def _handle_cancelar_form(self):
        """Notifica o controller principal para voltar à tela de lista ou inicial."""
        # Por padrão, volta para a lista de colaboradores.
        self.main_controller.mostrar_tela("lista_colaboradores")

    def _handle_atualizar_lista_colab(self):
        """chama o metodo para recarregar a lista de colaboradores."""
        self.main_controller.recarregarLista()

    def criar_lista_colaboradores(self, colaboradores_data):
        print("Dados recebidos:", colaboradores_data)
        """Cria a lista de colaboradores recuperando dados do MySQL"""

        self.limpar_container()

        frame = ttk.Frame(self.container, padding=20, style="Background.TFrame")
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Gerenciar Colaboradores",
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
            "data_admissao",
            "nivel_sistema",
            "cargo",
            "telefone",
            "endereco",
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
        self.tree.heading("data_admissao", text="Data Admissão", anchor="w")
        self.tree.heading("nivel_sistema", text="Nível Sistema", anchor="w")
        self.tree.heading("cargo", text="Cargo", anchor="w")
        self.tree.heading("telefone", text="Telefone", anchor="w")
        self.tree.heading("endereco", text="Endereço", anchor="w")

        # Configura as colunas
        self.tree.column("cpf", width=120, stretch=False)
        self.tree.column("nome", width=200, stretch=True)
        self.tree.column("data_admissao", width=200, stretch=False)
        self.tree.column("nivel_sistema", width=120, stretch=False)
        self.tree.column("cargo", width=150, stretch=False)
        self.tree.column("telefone", width=120, stretch=False)
        self.tree.column("endereco", width=200, stretch=True)

        self.tree.pack(fill="both", expand=True)

        # Preenche a treeview com os dados
        for colab in colaboradores_data:
            nivel_sistema = (
                NivelSistema(colab["nivelSistem"]).name.replace("_", " ")
                if colab["nivelSistem"]
                else ""
            )

            self.tree.insert(
                "",
                "end",
                values=(
                    colab["cpf"],
                    colab["nome"],
                    colab["data_admissao"],
                    nivel_sistema,
                    colab["funcao"],
                    colab["telefone_info"],
                    colab["endereco_info"],
                ),
            )

        btn_frame = ttk.Frame(frame, style="Background.TFrame")
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Adicionar Novo",
            command=lambda: self.main_controller.mostrar_tela(
                "form_colaborador", modo="novo"
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
            command=self._handle_atualizar_lista_colab,  # Agora recarrega os dados diretamente
            style="TButton",
        ).pack(side="left", padx=5)

    def _handle_editar_selecionado(self):
        """Solicita ao controller principal para mostrar o formulário de edição."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning(
                "Nenhuma Seleção", "Selecione um colaborador para editar."
            )
            return
        item_id_str = self.tree.item(selected_items[0])["values"][0]
        try:
            item_id = int(item_id_str)
            self.main_controller.solicitar_edicao_colaborador(item_id)
        except (ValueError, TypeError):
            messagebox.showerror("Erro", f"ID inválido: {item_id_str}")

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
        nome_colaborador = item_values[1]
        try:
            item_id = item_id_str
            self.main_controller.solicitar_exclusao_colaborador(
                item_id, nome_colaborador
            )
        except (ValueError, TypeError):
            messagebox.showerror("Erro", f"CPF inválido: {item_id_str}")
