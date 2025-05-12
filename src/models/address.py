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
