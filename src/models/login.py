import mysql, mysql.connector
from src.database.connectFromDB import Database


class Login:
    """
    Classe responsável pelas operações de login no sistema.

    Atributos:
        db (Database): Instância da conexão com o banco de dados.
    """

    def __init__(self):
        """
        Inicializa a classe Login com a conexão ao banco de dados.

        Args:
            db (Database): Instância da classe de conexão com o banco de dados.
        """
        self.db = Database()

    def add_login(self, cpf: str, password: str):
        """
        Adiciona um novo usuário na tabela de login do banco de dados.

        Args:
            cpf (str): CPF do usuário (somente números).
            password (str): Senha do usuário.
        """
        sql = "INSERT INTO Login (cpf, senha) VALUES (%s, %s)"
        params = (cpf, password)
        self.db.cursor.execute(sql, params)

    def validate_login(self, cpf: str, password: str) -> bool:
        """
        Valida se o login do usuário (CPF e senha) existe na base de dados.

        Args:
            cpf (str): CPF do usuário.
            password (str): Senha do usuário.

        Returns:
            bool: True se o usuário existe e os dados estão corretos, False caso contrário.

        raise:
            Lança uma exeção mysql.connector.Error caso haja um erro na verificação
        """
        try:
            if not self.db.connection.is_connected():
                self.db.connection.reconnect()
                self.db.cursor = self.db.connection.cursor(dictionary=True)

            sql = "SELECT * FROM login WHERE cpf = %s AND senha = %s"
            params = (cpf, password)
            self.db.cursor.execute(sql, params)
            resultado = self.db.cursor.fetchone()
            self.db.fecharConexao()
            return resultado if resultado else None
        except mysql.connector.Error as e:
            self.db.fecharConexao()
            raise ValueError(f"❌ Erro ao verificar login : \a {e}")

    def searchDataFromPerson(self, cpf: str, colaborador: bool = True) -> dict:
        """Metodo para recuperar os dados de uma pessoa do banco

        args:
            cpf(str): chave para verificar a pessoa no banco
            colaborador(boll): valor booleano para escolher a tabela da pessoa

        returns:
            dict: retorna um dicionario com a pessoa encontrada

        raise:
            lança uma exeção caso ocorra algum erro na consulta
        """
        try:
            person: dict = {}
            tabela: str = "colaboradores" if colaborador else "clientes"

            if not self.db.connection.is_connected():
                self.db.connection.reconnect()
                self.db.cursor = self.db.connection.cursor(dictionary=True)

            # verificação do valor da tabela
            if tabela not in ("colaboradores", "cliente"):
                raise ValueError("❌Tabela invalida!")

            sql = f"SELECT * FROM {tabela} WHERE cpf = %s"
            self.db.cursor.execute(sql, (cpf,))
            person["pessoa"] = self.db.cursor.fetchone()

            self.db.fecharConexao()

            return person if person else None
        except mysql.connector.Error as e:
            raise RuntimeError(f"❌Erro ao verificar a Pessoa: {e}")
