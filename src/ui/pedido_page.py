import tkinter as tk
from tkinter import ttk, messagebox


class PedidoPage:
    def __init__(self, container, limpar_container, main_controller, cor_fundo_janela):
        # Configuração inicial do frame
        self.container = container
        self.limpar_container = limpar_container  # Função para limpar o container
        self.main_controller = main_controller  # Controlador principal
        self.cor_fundo_janela = cor_fundo_janela  # Cor de fundo
        self.tree = None  # Referência para a Treeview
        self._pedidos_data = {}

    def criar_lista_pedidos(self, pedidos_data):
        """Cria a interface gráfica com a lista de pedidos.

        Args:
            pedidos_data (dict): Dicionário no formato:
                {
                    id_pedido: {
                        'numero_da_mesa': int,
                        'nome_do_colaborador': str,
                        'status_pedido': str,
                        'pratos': [{'prato': str, 'ingredientes': list}]
                    },
                }
        """
        # Limpa o container anterior
        self.limpar_container()

        # Armazena os dados recebidos
        self._pedidos_data = pedidos_data.copy()

        # Cria o frame principal
        frame = ttk.Frame(self.container, padding=20, style="Background.TFrame")
        frame.pack(fill="both", expand=True)

        # Título da página
        ttk.Label(
            frame,
            text="Pedidos",
            style="Subtitle.TLabel",
            background=self.cor_fundo_janela,
        ).pack(pady=(0, 15), anchor="w")

        # Container para a Treeview e scrollbar
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        # Definição das colunas
        columns = (
            "id",
            "mesa",
            "atendente",
            "pratos",
            "status",
        )
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            style="Treeview",
        )
        scrollbar.config(command=self.tree.yview)

        # Configuração do cabeçalho
        for col, title, width in [
            ("id", "ID", 50),
            ("mesa", "N° Mesa", 80),
            ("atendente", "Atendente", 120),
            ("pratos", "Pratos", 200),
            ("status", "Status", 100),
        ]:
            self.tree.heading(col, text=title, anchor="w")
            self.tree.column(col, width=width, stretch=(col != "id"))

        self.tree.pack(fill="both", expand=True)

        # Preenchimento dos dados
        for pedido_id, dados in pedidos_data.items():
            # Formata a lista de pratos para exibição
            lista_pratos = "\n".join([prato["prato"] for prato in dados["pratos"]])

            self.tree.insert(
                "",
                "end",
                values=(
                    pedido_id,  # id
                    dados["numero_da_mesa"],  # mesa
                    dados["nome_do_colaborador"],  # atendente
                    lista_pratos,  # pratos (um por linha)
                    dados["status_pedido"].capitalize(),  # status
                ),
                tags=(dados["status_pedido"],),  # Tag para estilização
            )

        # Configura cores por status
        self.tree.tag_configure("pendente", background="#fff3cd")
        self.tree.tag_configure("em_preparo", background="#cce5ff")
        self.tree.tag_configure("pronto", background="#d4edda")
        self.tree.tag_configure("entregue", background="#f8f9fa")

        # Configuração do evento de clique
        self.tree.bind("<ButtonRelease-1>", self._on_pedido_click)

        # Botões de ação
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=(10, 0))

        botoes = [
            ("Adicionar Pedido", self._handler_adicionar_pedido),
            ("Editar Pedido", self._handler_editar_pedido),
            ("Excluir Pedido", self._handler_excluir_pedido),
            (
                "Atualizar Pedidos",
                lambda: self.main_controller.recarregarListaPedidos(),
            ),
        ]

        for texto, comando in botoes:
            ttk.Button(
                btn_frame,
                text=texto,
                command=comando,
                style="TButton",
            ).pack(side="left", padx=5)

    def criar_form_pedido(
        self,
        modo="novo",
        data_pedido=None,
        data_pratos=None,
        id_colaborador: int = None,
        pedido_id: int = None,
    ):
        self.limpar_container()

        frame = ttk.Frame(self.container, padding=20, style="Background.TFrame")
        frame.pack(fill="both", expand=True)

        # Título dinâmico
        titulo = "Novo Pedido" if modo == "novo" else "Editar Pedido"
        ttk.Label(
            frame,
            text=titulo,
            style="Subtitle.TLabel",
            background=self.cor_fundo_janela,
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        # Campos do formulário
        campos = [
            ("Número da Mesa:", "numero_mesa"),
            ("Status:", "status"),
        ]

        self.entries = {}
        for i, (label_text, field_key) in enumerate(campos):
            ttk.Label(frame, text=label_text).grid(
                row=i + 1, column=0, sticky="w", padx=5, pady=8
            )

            if field_key == "status":  # Combobox para status
                entry = ttk.Combobox(
                    frame,
                    width=37,
                    values=[
                        "pendente",
                        "em preparo",
                        "pronto",
                        "entregue",
                        "cancelado",
                    ],
                )

            else:
                entry = ttk.Entry(frame, width=40, style="TEntry")

            entry.grid(row=i + 1, column=1, sticky="ew", padx=5, pady=8)
            self.entries[field_key] = entry

        # Lista de pratos
        ttk.Label(
            frame,
            text="Pratos:",
            style="TLabel",
            background=self.cor_fundo_janela,
        ).grid(row=4, column=0, sticky="nw", padx=(5, 10), pady=8)

        listbox_frame = ttk.Frame(frame)
        listbox_frame.grid(row=4, column=1, sticky="nsew", pady=8)

        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical")
        self.pratos_listbox = tk.Listbox(
            listbox_frame,
            selectmode="multiple",
            height=8,
            exportselection=False,
            yscrollcommand=scrollbar.set,
            bg="#ffffff",
            relief="solid",
            borderwidth=1,
        )
        scrollbar.config(command=self.pratos_listbox.yview)
        self.pratos_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Carrega pratos disponíveis
        pratos_disponiveis = data_pratos
        for prato in pratos_disponiveis:
            self.pratos_listbox.insert(
                "end", f"{prato['id']} - {prato['nome']} - R${prato['preco']}"
            )

        # Botões de ação
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0), sticky="e")

        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self._handle_cancelar_form_pedido,
            style="Secondary.TButton",
        ).pack(side="right", padx=5)

        ttk.Button(
            btn_frame,
            text="Salvar" if modo == "novo" else "Atualizar",
            command=lambda: self._handler_salvar_pedido(
                modo, id_colaborador, pedido_id
            ),
            style="Primary.TButton",
        ).pack(side="right", padx=5)

        # Preenchimento em modo edição
        if modo == "editar" and data_pedido and data_pratos:
            self.pedido_id_editando = pedido_id
            self.entries["numero_mesa"].insert(0, data_pedido.get("numero_da_mesa", ""))
            self.entries["status"].set(data_pedido.get("status_pedido", ""))

            # Seleciona pratos no listbox com base nos pratos já associados ao pedido
            pratos_selecionados = [
                prato.get("id")
                for prato in data_pedido.get("pratos", [])
                if isinstance(prato, dict) and "id" in prato
            ]

            for i in range(self.pratos_listbox.size()):
                item_text = self.pratos_listbox.get(i)
                if any(str(prato_id) in item_text for prato_id in pratos_selecionados):
                    self.pratos_listbox.selection_set(i)
        frame.columnconfigure(1, weight=1)

    def _on_pedido_click(self, event):
        """Handler para clique nos itens da Treeview."""
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(
            event.x
        )  # Mudei para event.x para identificar a coluna corretamente

        # Verifica se o clique foi na coluna de pratos (índice 4)
        if item and column == "#4":
            # Obtém o ID do pedido
            pedido_id = self.tree.item(item)["values"][0]

            # Obtém os dados completos do pedido
            pedido = self._pedidos_data.get(pedido_id)
            # print(pedido)

            if pedido:
                self._mostrar_detalhes_pedido(pedido)

    def _mostrar_detalhes_pedido(self, pedido):
        """Mostra os detalhes completos do pedido em uma nova janela."""
        # Criar janela de detalhes
        detail_window = tk.Toplevel(self.container)
        detail_window.title(
            f"Detalhes do Pedido da Mesa #{pedido.get('numero_da_mesa', '')}"
        )

        # Frame principal
        frame = ttk.Frame(detail_window, padding=50)
        frame.pack(fill="both", expand=True)

        # Informações básicas
        ttk.Label(frame, text=f"Mesa: {pedido.get('numero_da_mesa', '')}").pack(
            anchor="w"
        )
        ttk.Label(
            frame, text=f"Atendente: {pedido.get('nome_do_colaborador', '')}"
        ).pack(anchor="w")
        ttk.Label(
            frame, text=f"Status: {pedido.get('status_pedido', '').capitalize()}"
        ).pack(anchor="w")

        # Lista de pratos com ingredientes
        ttk.Label(frame, text="Pratos:", style="Bold.TLabel").pack(
            anchor="w", pady=(10, 0)
        )

        for prato in pedido.get("pratos", []):
            # Frame para cada prato
            prato_frame = ttk.Frame(frame, borderwidth=1, relief="solid", padding=5)
            prato_frame.pack(fill="x", pady=2)

            # Nome do prato
            ttk.Label(
                prato_frame, text=prato.get("prato", ""), style="Bold.TLabel"
            ).pack(anchor="w")

            # Ingredientes
            ingredientes_frame = ttk.Frame(prato_frame)
            ingredientes_frame.pack(anchor="w", padx=10)

            for ingrediente in prato.get("ingredientes", []):
                ttk.Label(ingredientes_frame, text=f"• {ingrediente}").pack(anchor="w")

    # Métodos de handlers
    def _handler_adicionar_pedido(self):
        """Abre o formulário para novo pedido"""
        self.main_controller.mostrar_tela("form_pedido", modo="novo")

    def _handler_editar_pedido(self):
        """Edita o pedido selecionado"""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Nenhum pedido selecionado!")
            return

        pedido_id = self.tree.item(selecionado[0])["values"][0]
        self.main_controller.solicitar_edicao_pedido(pedido_id)

    def _handler_excluir_pedido(self):
        """Exclui o pedido selecionado"""
        selecionado = self.tree.selection()

        if not selecionado:
            messagebox.showwarning("Aviso", "Nenhum pedido selecionado!")
            return

        pedido_id = self.tree.item(selecionado[0])["values"][0]
        nome_pedido = self.tree.item(selecionado[0])["values"][1]
        if messagebox.askyesno(
            "Confirmar",
            f"Excluir pedido {pedido_id} da mesa {nome_pedido}?",
        ):
            self.main_controller.solicitar_exclusao_pedido(pedido_id)

    def _handler_salvar_pedido(self, modo, id_colaborador, id_pedido: int = None):
        # Coleta os dados do formulário
        dados = {
            "numero_mesa": self.entries["numero_mesa"].get(),
            "id_colaborador": id_colaborador,
            "status": self.entries["status"].get(),
            "pratos": [
                self.pratos_listbox.get(i).split(" - ")[0]
                for i in self.pratos_listbox.curselection()
            ],
        }

        # print(dados)

        if modo == "editar":
            self.main_controller.atualizar_pedido(id_pedido, dados)
        else:
            self.main_controller.criar_pedido(dados)

        self.limpar_container()
        self.main_controller.recarregarListaPedidos()

    def _handle_cancelar_form_pedido(self):
        """Notifica o controller principal para voltar à tela de lista."""
        # Por padrão, volta para a lista de pratos.
        self.main_controller.mostrar_tela("lista_pedidos")
