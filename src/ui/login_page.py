from tkinter import messagebox, ttk


class LoginPage:
    def __init__(
        self,
        container,
        limpar_container,
        main_controller,  # Instância da classe Main
        cor_fundo_janela,
    ):
        self.container = container
        self.limpar_container = limpar_container
        self.main_controller = main_controller
        self.cor_fundo_janela = cor_fundo_janela

        # Inicialização padrão dos atributos que serão usados
        self.entries = {}
        self.cpf_entry_login = None
        self.senha_entry_login = None

    def criar_tela_login(self):
        """Tela de login do Sistema"""
        self.limpar_container()

        login_frame = ttk.Frame(self.container, style="Background.TFrame")
        login_frame.pack(expand=True)

        frame = ttk.Frame(login_frame, padding=(30, 20), style="TFrame")
        frame.grid(row=0, column=0)

        title_login = "Faça o login com seu CPF e SENHA"
        ttk.Label(frame, text=title_login, style="Subtitle.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 25), sticky="w"
        )

        labels = ["CPF", "SENHA"]
        self.entries = {}

        for i, label_text in enumerate(labels):
            ttk.Label(frame, text=label_text).grid(
                row=i + 1, column=0, sticky="w", padx=5, pady=8
            )
            entry = ttk.Entry(
                frame,
                width=40,
                style="TEntry",
                show="*" if label_text == "SENHA" else "",
            )
            entry.grid(row=i + 1, column=1, sticky="ew", padx=5, pady=8)
            self.entries[label_text] = entry

        self.cpf_entry_login = self.entries["CPF"]
        self.senha_entry_login = self.entries["SENHA"]

        btn_frame_login = ttk.Frame(frame, style="TFrame")
        btn_frame_login.grid(
            row=len(labels) + 1, column=0, columnspan=2, pady=(30, 10), sticky="e"
        )

        ttk.Button(
            btn_frame_login,
            text="Login",
            style="TButton",
            command=self._handle_login_attempt,
        ).pack(side="left", padx=(0, 10))

        frame.columnconfigure(1, weight=1)

    def _handle_login_attempt(self):
        """Coleta dados e chama o controller principal para tentar o login."""
        cpf = self.cpf_entry_login.get()
        senha = self.senha_entry_login.get()
        self.main_controller.tentar_login(cpf, senha)
