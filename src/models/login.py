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
        try:
            self.db.abrirConexao()
            sql = "INSERT INTO login (cpf, senha) VALUES (%s, %s)"
            params = (
                cpf,
                password,
            )
            self.db.cursor.execute(sql, params)
            self.db.connection.commit()
        except mysql.connector.Error as e:
            raise ValueError(f"❌ Erro ao inserir login : \a {e}")
        finally:
            self.db.fecharConexao()

    def validate_login(self, cpf: str, password: str) -> dict:
        """
        Valida se o CPF existe e se a senha está correta.

        Args:
        cpf (str): CPF do usuário.
        password (str): Senha informada pelo usuário.

        Returns:
        dict: {
            'cpf_exists': bool,        # True se o CPF estiver cadastrado
            'correct_password': bool   # True se a senha conferiu (só avaliado se cpf_exists for True)
        }

        Raises:
        mysql.connector.Error: Em caso de falha na consulta ao banco.
        """
        try:
            self.db.abrirConexao()

            # 1) Verifica existência do CPF e obtém a senha cadastrada
            sql = "SELECT senha FROM login WHERE cpf = %s"
            self.db.cursor.execute(sql, (cpf,))
            row = self.db.cursor.fetchone()

            # Se não achou, retorna flags: CPF não existe
            if row is None:
                return {"cpf_exists": False, "correct_password": False}

            # CPF existe
            db_senha = row["senha"]

            # 2) Compara senhas
            correct = str(password) == str(db_senha)

            return {"cpf_exists": True, "correct_password": correct}

        except mysql.connector.Error as e:
            # propagando erro de banco
            raise RuntimeError(f"Erro ao verificar login: {e.msg}") from e

        finally:
            self.db.fecharConexao()

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
