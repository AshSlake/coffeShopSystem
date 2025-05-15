import tkinter as tk
from tkinter import ttk, messagebox


class PratosPage:
    def __init__(self, container, limpar_container, main_controller, cor_fundo_janela):
        self.container = container
        self.limpar_container = limpar_container
        self.main_controller = main_controller
        self.cor_fundo_janela = cor_fundo_janela

        self.entries = {}
        self.tree = None
        self.ing_listbox = None

    def criar_form_pratos(self, modo="novo", data_prato=None):
        self.limpar_container()

        frame = ttk.Frame(self.container, padding=20, style="Background.TFrame")
        frame.pack(fill="both", expand=True)

        titulo = "Cadastrar Novo Prato" if modo == "novo" else "Editar Prato"
        ttk.Label(frame, text=titulo, style="Subtitle.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 20), sticky="w"
        )

        labels_fields = [
            ("Nome:", "nome"),
            ("Preço:", "preco"),
        ]
        self.entries = {}
        for i, (label_text, field_key) in enumerate(labels_fields):
            ttk.Label(frame, text=label_text).grid(
                row=i + 1, column=0, sticky="w", padx=5, pady=8
            )
            entry = ttk.Entry(frame, width=40, style="TEntry")
            entry.grid(row=i + 1, column=1, sticky="ew", padx=5, pady=8)
            self.entries[field_key] = entry

        # Ingredientes (Listbox)
        ttk.Label(frame, text="Ingredientes:").grid(
            row=3, column=0, sticky="nw", padx=5, pady=8
        )
        self.ing_listbox = tk.Listbox(frame, selectmode="multiple", height=6)
        self.ing_listbox.grid(row=3, column=1, sticky="ew", padx=5, pady=8)

        ingredientes_disponiveis = self.main_controller.recuperar_ingredientes()
        for ing in ingredientes_disponiveis:
            self.ing_listbox.insert("end", f"{ing['id']} - {ing['nome']}")

        # Preenche se estiver editando
        if modo == "editar" and data_prato:
            self.prato_id_editando = data_prato.get("id")
            self.entries["nome"].insert(0, data_prato.get("nome", ""))
            self.entries["preco"].insert(0, data_prato.get("preco", ""))

            ingredientes_str = data_prato.get("ingredientes", "")
            ingredientes_ids = set()
            for ing_nome in ingredientes_str.split(", "):
                for i in range(self.ing_listbox.size()):
                    item_text = self.ing_listbox.get(i)
                    if ing_nome in item_text:
                        self.ing_listbox.selection_set(i)
                        break

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0), sticky="e")

        ttk.Button(
            btn_frame,
            text="Salvar",
            command=lambda: self._handle_salvar_prato(modo),
            style="TButton",
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=lambda: self._handle_cancelar_form_prato(),
            style="TButton",
        ).pack(side="left")

    def _handle_salvar_prato(self, modo):
        prato_id = getattr(self, "prato_id_editando", None)
        nome = self.entries["nome"].get()
        preco = self.entries["preco"].get()
        sel = self.ing_listbox.curselection()
        ingrediente_ids = [int(self.ing_listbox.get(i).split(" - ")[0]) for i in sel]

        if not nome or not preco or not ingrediente_ids:
            messagebox.showerror(
                "Erro",
                "Preencha todos os campos e selecione pelo menos um ingrediente.",
            )
            return

        dados = {
            "id": prato_id,
            "nome": nome,
            "preco": preco,
            "ingredientes": ingrediente_ids,
        }

        self.main_controller.salvar_dados_prato(dados, modo)

    def criar_lista_pratos(self, pratos_data):
        self.limpar_container()

        frame = ttk.Frame(self.container, padding=20, style="Background.TFrame")
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Gerenciar Pratos",
            style="Subtitle.TLabel",
            background=self.cor_fundo_janela,
        ).pack(pady=(0, 15), anchor="w")

        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        columns = ("id", "nome", "preco", "ingredientes")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            style="Treeview",
        )
        scrollbar.config(command=self.tree.yview)

        for col, title, width in [
            ("id", "ID", 50),
            ("nome", "Nome", 200),
            ("preco", "Preço", 80),
            ("ingredientes", "Ingredientes", 300),
        ]:
            self.tree.heading(col, text=title, anchor="w")
            self.tree.column(col, width=width, stretch=(col != "id"))

        self.tree.pack(fill="both", expand=True)

        for prato in pratos_data:
            self.tree.insert(
                "",
                "end",
                values=(
                    prato["id"],
                    prato["nome"],
                    prato["preco"],
                    prato["ingredientes"],
                ),
            )

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Adicionar Novo",
            command=lambda: self.main_controller.mostrar_tela(
                "form_prato", modo="novo"
            ),
            style="TButton",
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Editar Selecionado",
            command=lambda: self._handle_editar_selecionado(),
            style="TButton",
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Excluir Selecionado",
            command=lambda: self._handle_excluir_selecionado(),
            style="TButton",
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Atualizar Lista",
            command=lambda: self.main_controller.recarregarListaPratos(),
            style="TButton",
        ).pack(side="left", padx=5)

    def _handle_editar_selecionado(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Seleção", "Selecione um prato para editar.")
            return

        prato_id = self.tree.item(selected_items[0])["values"][0]
        self.main_controller.solicitar_edicao_prato(prato_id)

    def _handle_excluir_selecionado(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Seleção", "Selecione um prato para excluir.")
            return

        prato_id = self.tree.item(selected_items[0])["values"][0]
        nome_prato = self.tree.item(selected_items[0])["values"][1]

        if messagebox.askyesno(
            "Confirmar Exclusão", f"Deseja excluir o prato '{nome_prato}'?"
        ):
            self.main_controller.solicitar_exclusao_prato(prato_id)

    def _handle_cancelar_form_prato(self):
        """Notifica o controller principal para voltar à tela de lista."""
        # Por padrão, volta para a lista de pratos.
        self.main_controller.mostrar_tela("lista_pratos")
