import mysql, mysql.connector

from src.database.connectFromDB import Database


class Address:
    def __init__(self, db: Database):
        self.db = db

    def inserirEndereco(self, endereco: str = None):
        """
        Insere um endereço no banco de dados.

        Args:
            endereco (str): Endereço do colaborador.

        Returns:
            int: ID do novo endereço inserido no banco de dados, ou None se falhar.

        Raises:
            mysql.connector.Error: Se ocorrer erro durante a inserção.
        """

        try:
            if endereco and endereco.strip():
                sql = "INSERT INTO enderecos(endereco) VALUES(%s);"
                data: tuple = (endereco,)
                self.db.cursor.execute(sql, data)
                self.db.connection.commit()
                newID = self.db.cursor.lastrowid
                print("✅ Endereco inserido com sucesso")
                return newID
            else:
                print("⚠️ Campo endereco foi fornecido vazio.")
                return None  # Retornar None para indicar falha ou ausência de inserção
        except mysql.connector.Error as e:
            print(f"❌ Erro ao inserir endereco na tabela: \n{e}")

    def AtualizarEndereco(self, id_endereco: int, novo_endereco: str):
        """
        atualiza o endereço do cliente

        Args:
            id_endereco (int) : id do endereco a ser atualizado
            novo_endereco (str) : novo endereco a ser atualizado,

        Raises:
            mysql.connector.Error: Se ocorrer erro durante a inserção.
        """

        try:
            valores_dict = {}
            if id_endereco is not None:
                valores_dict["id_endereco"] = id_endereco
            if novo_endereco and novo_endereco.strip():
                valores_dict["enderedo"] = novo_endereco

            self.db.atualizarRegistro(
                "enderecos", valores_dict, "id_endereco", id_endereco
            )
        except mysql.connector.Error as e:
            print("❌ ocorreu um erro ao atualizar o Endereço.")

    def buscar_endereco_por_id(
        self, ids_endereco: int | list[int]
    ) -> dict | list[dict]:
        """
        Busca endereço(s) pelo(s) ID(s) na tabela 'enderecos'.

        Este método aceita tanto um único ID quanto uma lista de IDs.
        Se for passado um único ID, retorna um único dicionário.
        Se for passada uma lista de IDs, retorna uma lista de dicionários.

        Args:
            ids_endereco (int | list[int]): ID único ou lista de IDs de endereços a serem buscados.

        Returns:
            dict | list[dict]:
                - Um dicionário com os dados do endereço, se for ID único.
                  Exemplo: {'id_endereco': 1, 'endereco': 'Rua Exemplo, 123'}
                - Uma lista de dicionários com os dados dos endereços, se for uma lista de IDs.

        Raises:
            mysql.connector.Error: Se ocorrer erro na consulta ao banco de dados.
        """
        try:
            self.db.cursor = self.db.connection.cursor(dictionary=True)

            if isinstance(ids_endereco, list):
                if not ids_endereco:
                    return []
                placeholders = ", ".join(["%s"] * len(ids_endereco))
                sql = f"SELECT * FROM enderecos WHERE id_endereco IN ({placeholders})"
                self.db.cursor.execute(sql, ids_endereco)
                return self.db.cursor.fetchall()

            sql = "SELECT * FROM enderecos WHERE id_endereco = %s"
            self.db.cursor.execute(sql, (ids_endereco,))
            endereco = self.db.cursor.fetchone()

            if endereco:
                print(f"✅ Endereço encontrado: ID {ids_endereco}")
                return endereco
            else:
                print(f"⚠️ Endereço com ID {ids_endereco} não encontrado")
                return None

        except mysql.connector.Error as e:
            print(f"❌ Erro ao buscar endereço por ID: \n{e}")
            raise
        finally:
            if hasattr(self.db, "cursor") and self.db.cursor:
                self.db.cursor.close()

    def deletarEndereco(self, id_endereco: int):
        """Deleta um endereço do banco de dados.

        Args:
            id_endereco (int): id do endereço a ser deletado.

        Raises:
            mysql.connector.Error: Se ocorrer erro ao deletar o cliente.
        """
        try:
            sql = "DELETE FROM enderecos WHERE id_endereco = %s"
            self.db.cursor.execute(sql, (id_endereco,))
            self.db.connection.commit()
            print(f"✅ Endereço com id({id_endereco}) deletado com sucesso.")
        except mysql.connector.Error as e:
            print(f"❌ Erro ao deletar o Endereço: \n {e}")
