# SESSÃO INGREDIENTES
import mysql, mysql.connector
from ConnectFromDB import Database


class Ingredients:
    def __init__(self, db: Database):
        self.db = db

    def inserirIngrediente(self, nome: str):
        """
        Insere um novo ingrediente na tabela Ingredientes.

        Args:
            nome (str): O nome do ingrediente.

        Returns:
            int | None: O ID do ingrediente recém-inserido, ou None em caso de falha.

        Raises:
            mysql.connector.Error: Se ocorrer um erro ao executar a inserção no banco.
        """
        try:
            sql = "INSERT INTO Ingredientes (nome) VALUES (%s)"
            self.db.cursor.execute(sql, (nome,))
            self.db.connection.commit()
            newID = self.db.cursor.lastrowid
            print(f"✅ Ingrediente (ID: {newID}, Nome: {nome}) inserido com sucesso.")
            return newID
        except mysql.connector.Error as e:
            print(f"❌ Erro ao inserir ingrediente: \n{e}")
            return None

    def atualizarIngrediente(self, id_ingrediente: int, novo_nome: str):
        """
        Atualiza o nome de um ingrediente existente.

        Args:
            id_ingrediente (int): O ID do ingrediente a ser atualizado.
            novo_nome (str): O novo nome do ingrediente.

        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer um erro durante a atualização.
        """
        try:
            self.db.atualizarRegistro(
                "Ingredientes", {"nome": novo_nome}, "id", id_ingrediente
            )
            return True
        except mysql.connector.Error as e:
            return False

    def deletarIngrediente(self, id_ingrediente: int):
        """
        Deleta um ingrediente da tabela Ingredientes.
        Atenção: Se este ingrediente estiver sendo usado em Prato_Ingredientes,
        a deleção pode falhar a menos que ON DELETE CASCADE esteja configurado
        ou as associações sejam removidas primeiro.

        Args:
            id_ingrediente (int): O ID do ingrediente a ser deletado.

        Returns:
            bool: True se a deleção foi bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer um erro durante a deleção.
        """
        try:
            # Primeiro, remover das associações em Prato_Ingredientes
            sql_remove_assoc = (
                "DELETE FROM Prato_Ingredientes WHERE ingrediente_id = %s"
            )
            self.db.cursor.execute(sql_remove_assoc, (id_ingrediente,))
            # Não precisa de commit aqui se o próximo comando for na mesma transação (auto-commit off)
            # Mas para garantir, vamos commitar se houver auto-commit ou fazer tudo em uma transação explícita.
            self.db.connection.commit()  # Depende da configuração de auto-commit

            sql = "DELETE FROM Ingredientes WHERE id = %s"
            self.db.cursor.execute(sql, (id_ingrediente,))
            self.db.connection.commit()  # Commit final
            if self.db.cursor.rowcount > 0:
                print(
                    f"✅ Ingrediente (ID: {id_ingrediente}) e suas associações deletados com sucesso."
                )
                return True
            else:
                print(
                    f"⚠️ Ingrediente (ID: {id_ingrediente}) não encontrado para deleção."
                )
                return False
        except mysql.connector.Error as e:
            print(f"❌ Erro ao deletar ingrediente (ID: {id_ingrediente}): \n{e}")
            self.db.connection.rollback()  # Se algo deu errado, desfazer
            return False
