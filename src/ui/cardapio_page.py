import tkinter as tk
from tkinter import ttk, messagebox


class CardapioPage:
    def __init__(
        self,
        container,
        limpar_container,
        main_controller,
        cor_fundo_janela,
    ):
        self.container = container
        self.limpar_container = limpar_container
        self.main_controller = main_controller
        self.cor_fundo_janela = cor_fundo_janela
        self.tree = None

    def criar_lista_cardapio(self, cardapio_data):
        """
        Exibe todos os pratos contidos em um cardápio específico do banco de dados.

        Args:
            cardapio_data (dict): {'id': cardapio_id,
                                   'pratos': [ {'id': int, 'nome': str, 'preco': Decimal}, ... ]}
        """
        self.limpar_container()

        frame = ttk.Frame(self.container, padding=20, style="Background.TFrame")
        frame.pack(fill="both", expand=True)

        card_id = int(cardapio_data.get("id"))
        titulo = f"Pratos do Cardápio {card_id}"
        ttk.Label(
            frame,
            text=titulo,
            style="Subtitle.TLabel",
            background=self.cor_fundo_janela,
        ).pack(pady=(0, 15), anchor="w")

        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        columns = ("id", "nome", "preco")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            style="Treeview",
        )
        scrollbar.config(command=self.tree.yview)

        # Cabeçalhos
        headers = [
            {"key": "id", "text": "ID", "width": 100, "stretch": False},
            {"key": "nome", "text": "Nome do Prato", "width": 250, "stretch": True},
            {"key": "preco", "text": "Preço", "width": 150, "stretch": False},
        ]

        for header in headers:
            self.tree.heading(header["key"], text=header["text"], anchor="w")
            self.tree.column(
                header["key"], width=header["width"], stretch=header["stretch"]
            )

        self.tree.pack(fill="both", expand=True)

        # Inserir dados
        for prato in cardapio_data.get("pratos", []):
            preco_str = (
                f"R$ {prato['preco']:.2f}" if prato.get("preco") is not None else "-"
            )
            self.tree.insert("", "end", values=(prato["id"], prato["nome"], preco_str))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Adicionar Prato",
            command=self._handle_adicionar_prato,
            style="TButton",
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Excluir Prato",
            command=lambda: self._handle_excluir_prato_selecionado(card_id),
            style="TButton",
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Atualizar Lista",
            command=lambda: self.main_controller.recarregar_pratos_cardapio(),
            style="TButton",
        ).pack(side="left", padx=5)

    def criar_view_add_Pratos(self, cardapio_id: int, data_pratos=None):
        self.limpar_container()
        print(data_pratos)

        frame = ttk.Frame(self.container, padding=20, style="Background.TFrame")
        frame.pack(fill="both", expand=True)

        # Título
        ttk.Label(
            frame,
            text="Adicionar Prato ao Cardápio",
            style="Subtitle.TLabel",
            background=self.cor_fundo_janela,
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        # Label
        ttk.Label(
            frame,
            text="Pratos disponíveis:",
            style="TLabel",
            background=self.cor_fundo_janela,
        ).grid(row=1, column=0, sticky="nw", padx=(0, 10), pady=8)

        # Listbox com Scrollbar
        listbox_frame = ttk.Frame(frame)
        listbox_frame.grid(row=1, column=1, sticky="nsew", pady=8)

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

        # Ajuste de coluna expansível
        frame.columnconfigure(1, weight=1)

        # Preenchendo os pratos
        if data_pratos:
            for prato in data_pratos:
                self.pratos_listbox.insert("end", f"{prato['id']} - {prato['nome']}")

        # Botões
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0), sticky="e")

        ttk.Button(
            btn_frame,
            text="Salvar",
            command=lambda: self._handle_salvar_prato(cardapio_id),
            style="TButton",
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self._handle_cancelar_add_prato,
            style="TButton",
        ).pack(side="left", padx=5)

    def _handle_adicionar_prato(self):
        self.main_controller.adicionar_prato_ao_cardapio()

    def _handle_excluir_prato_selecionado(self, cardapio_id: int):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Seleção", "Selecione um prato para excluir.")
            return
        prato_id = self.tree.item(selected[0])["values"][0]
        if messagebox.askyesno(
            "Confirmar Exclusão", f"Deseja remover o prato ID {prato_id} do cardápio?"
        ):
            # precisa do cardapio_id para remover, então recarrega após remover
            self.main_controller.remover_prato_do_cardapio(cardapio_id, prato_id)
            self.main_controller.recarregar_pratos_cardapio()

    def _handle_salvar_prato(self, cardapio_id: int) -> dict:
        """Solicita ao controlador que insira os pratos selecioando no cardapio.

        args:
            cardapio_id(int): id do cardapio para inserção dos pratos.

        returns:
            dict: retorna um dict com as chaves dos pratos para inserção.
        """
        item_selected = self.pratos_listbox.curselection()
        pratos_id = [
            int(self.pratos_listbox.get(i).split(" - ")[0]) for i in item_selected
        ]

        dados = {
            "pratos": pratos_id,
        }

        self.main_controller.salvar_prato_cardapio(cardapio_id, dados)
        self.main_controller.recarregar_pratos_cardapio()

    def _handle_cancelar_add_prato(self):
        """Notifica o controller principal para voltar para o cardapio."""
        self.main_controller.mostrar_tela("mostrar_cardapio")
