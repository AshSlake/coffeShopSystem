# SESSÃO CARDAPIO
import mysql, mysql.connector

from src.database.connectFromDB import Database


class Menu:
    def __init__(self, db: Database):
        self.db = db

    def criarCardapio(self):
        """
        Cria um novo cardápio (basicamente, insere um novo ID na tabela Cardapio).
        A tabela Cardapio conforme definida tem apenas um ID.

        Returns:
            int | None: O ID do cardápio recém-criado, ou None em caso de falha.

        Raises:
            mysql.connector.Error: Se ocorrer um erro ao executar a inserção no banco.
        """
        try:
            # Como a tabela Cardapio só tem ID (PK, assumed auto_increment),
            # um insert sem colunas específicas ou com DEFAULT VALUES funciona.
            # Para MySQL, se 'id' é AUTO_INCREMENT:
            sql = "INSERT INTO Cardapio () VALUES ()"  # Ou "INSERT INTO Cardapio (id) VALUES (NULL)"
            self.db.cursor.execute(sql)
            self.db.connection.commit()
            newID = self.cursor.lastrowid
            print(f"✅ Novo Cardápio (ID: {newID}) criado com sucesso.")
            return newID
        except mysql.connector.Error as e:
            print(f"❌ Erro ao criar novo cardápio: \n{e}")
            return None

    def adicionarPratoAoCardapio(self, cardapio_id: int, prato_id: int):
        """
        Associa um prato a um cardápio na tabela Cardapio_Pratos.

        Args:
            cardapio_id (int): O ID do cardápio.
            prato_id (int): O ID do prato.

        Returns:
            bool: True se a associação foi bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer um erro durante a inserção na tabela de junção.
        """
        try:
            sql = "INSERT INTO Cardapio_Pratos (cardapio_id, prato_id) VALUES (%s, %s)"
            self.db.cursor.execute(sql, (cardapio_id, prato_id))
            self.db.connection.commit()
            print(
                f"✅ Prato (ID: {prato_id}) adicionado ao Cardápio (ID: {cardapio_id}) com sucesso."
            )
            return True
        except mysql.connector.Error as e:
            print(
                f"❌ Erro ao adicionar prato (ID: {prato_id}) ao Cardápio (ID: {cardapio_id}): \n{e}"
            )
            return False

    def removerPratoDoCardapio(self, cardapio_id: int, prato_id: int):
        """
        Remove a associação de um prato a um cardápio da tabela Cardapio_Pratos.

        Args:
            cardapio_id (int): O ID do cardápio.
            prato_id (int): O ID do prato.

        Returns:
            bool: True se a remoção foi bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer um erro durante a deleção na tabela de junção.
        """
        try:
            sql = "DELETE FROM Cardapio_Pratos WHERE cardapio_id = %s AND prato_id = %s"
            self.db.cursor.execute(sql, (cardapio_id, prato_id))
            self.db.connection.commit()
            if self.db.cursor.rowcount > 0:
                print(
                    f"✅ Prato (ID: {prato_id}) removido do Cardápio (ID: {cardapio_id}) com sucesso."
                )
                return True
            else:
                print(
                    f"⚠️ Associação não encontrada para remover Prato (ID: {prato_id}) do Cardápio (ID: {cardapio_id})."
                )
                return False
        except mysql.connector.Error as e:
            print(
                f"❌ Erro ao remover prato (ID: {prato_id}) do Cardápio (ID: {cardapio_id}): \n{e}"
            )
            return False

    def deletarCardapio(self, id_cardapio: int):
        """
        Deleta um cardápio da tabela Cardapio e suas associações em Cardapio_Pratos.

        Args:
            id_cardapio (int): O ID do cardápio a ser deletado.

        Returns:
            bool: True se a deleção foi bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer um erro durante a deleção.
        """
        try:
            self.db.connection.start_transaction()
            # Remover de Cardapio_Pratos primeiro
            sql_remove_assoc = "DELETE FROM Cardapio_Pratos WHERE cardapio_id = %s"
            self.db.cursor.execute(sql_remove_assoc, (id_cardapio,))

            # Deletar o cardápio
            sql_delete_cardapio = "DELETE FROM Cardapio WHERE id = %s"
            self.db.cursor.execute(sql_delete_cardapio, (id_cardapio,))

            self.db.connection.commit()

            if self.db.cursor.rowcount > 0:  # Refere-se ao DELETE FROM Cardapio
                print(
                    f"✅ Cardápio (ID: {id_cardapio}) e seus pratos associados deletados com sucesso."
                )
                return True
            else:
                print(f"⚠️ Cardápio (ID: {id_cardapio}) não encontrado para deleção.")
                return False
        except mysql.connector.Error as e:
            self.db.connection.rollback()
            print(f"❌ Erro ao deletar cardápio (ID: {id_cardapio}): \n{e}")
            return False
