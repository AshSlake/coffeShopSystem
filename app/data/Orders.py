# SESSÃO PEDIDOS
import mysql, mysql.connector
from ConnectFromDB import Database


class Orders:
    def __init__(self, db: Database):
        self.db = db

    def inserirPedido(self, num_mesa: int, fk_colaborador: int):
        """
        Insere um novo pedido na tabela Pedidos.

        Args:
            num_mesa (int): O número da mesa para o pedido.
            fk_colaborador (int): O CPF do colaborador que registrou o pedido.

        Returns:
            int | None: O ID do pedido recém-inserido, ou None em caso de falha.

        Raises:
            mysql.connector.Error: Se ocorrer um erro ao executar a inserção no banco.
        """
        try:
            sql = "INSERT INTO Pedidos (numMesa, fk_colaborador) VALUES (%s, %s)"
            self.db.cursor.execute(sql, (num_mesa, fk_colaborador))
            self.db.connection.commit()
            newID = self.db.cursor.lastrowid
            print(f"✅ Pedido (ID: {newID}) para mesa {num_mesa} inserido com sucesso.")
            return newID
        except mysql.connector.Error as e:
            print(f"❌ Erro ao inserir pedido: \n{e}")
            return None

    def adicionarPratoAoPedido(self, pedido_id: int, prato_id: int):
        """
        Associa um prato a um pedido na tabela Pedido_Pratos.

        Args:
            pedido_id (int): O ID do pedido.
            prato_id (int): O ID do prato.

        Returns:
            bool: True se a associação foi bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer um erro durante a inserção na tabela de junção.
        """
        try:
            sql = "INSERT INTO Pedido_Pratos (pedido_id, prato_id) VALUES (%s, %s)"
            self.db.cursor.execute(sql, (pedido_id, prato_id))
            self.db.connection.commit()
            print(
                f"✅ Prato (ID: {prato_id}) adicionado ao Pedido (ID: {pedido_id}) com sucesso."
            )
            return True
        except mysql.connector.Error as e:
            print(
                f"❌ Erro ao adicionar prato (ID: {prato_id}) ao Pedido (ID: {pedido_id}): \n{e}"
            )
            return False

    def removerPratoDoPedido(self, pedido_id: int, prato_id: int):
        """
        Remove a associação de um prato a um pedido da tabela Pedido_Pratos.

        Args:
            pedido_id (int): O ID do pedido.
            prato_id (int): O ID do prato.

        Returns:
            bool: True se a remoção foi bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer um erro durante a deleção na tabela de junção.
        """
        try:
            sql = "DELETE FROM Pedido_Pratos WHERE pedido_id = %s AND prato_id = %s"
            self.db.cursor.execute(sql, (pedido_id, prato_id))
            self.db.connection.commit()
            if self.db.cursor.rowcount > 0:
                print(
                    f"✅ Prato (ID: {prato_id}) removido do Pedido (ID: {pedido_id}) com sucesso."
                )
                return True
            else:
                print(
                    f"⚠️ Associação não encontrada para remover Prato (ID: {prato_id}) do Pedido (ID: {pedido_id})."
                )
                return False
        except mysql.connector.Error as e:
            print(
                f"❌ Erro ao remover prato (ID: {prato_id}) do Pedido (ID: {pedido_id}): \n{e}"
            )
            return False

    def atualizarPedido(
        self, id_pedido: int, novo_num_mesa: int = None, novo_fk_colaborador: int = None
    ):
        """
        Atualiza os dados de um pedido existente.

        Args:
            id_pedido (int): O ID do pedido a ser atualizado.
            novo_num_mesa (int, optional): O novo número da mesa.
            novo_fk_colaborador (int, optional): O novo CPF do colaborador.

        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer um erro durante a atualização.
        """
        valores_dict = {}
        if novo_num_mesa is not None:
            valores_dict["numMesa"] = novo_num_mesa
        if novo_fk_colaborador is not None:
            valores_dict["fk_colaborador"] = novo_fk_colaborador

        if valores_dict:
            try:
                self.db.atualizarRegistro(
                    "Pedidos", valores_dict, "id_pedido", id_pedido
                )
                return True
            except mysql.connector.Error as e:
                return False
        else:
            print("⚠️ Nenhum campo fornecido para atualizar o pedido.")
            return False

    def deletarPedido(self, id_pedido: int):
        """
        Deleta um pedido da tabela Pedidos e suas associações em Pedido_Pratos.

        Args:
            id_pedido (int): O ID do pedido a ser deletado.

        Returns:
            bool: True se a deleção foi bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer um erro durante a deleção.
        """
        try:
            self.db.connection.start_transaction()
            # Remover de Pedido_Pratos primeiro
            sql_remove_assoc = "DELETE FROM Pedido_Pratos WHERE pedido_id = %s"
            self.db.cursor.execute(sql_remove_assoc, (id_pedido,))

            # Deletar o pedido
            sql_delete_pedido = "DELETE FROM Pedidos WHERE id_pedido = %s"
            self.db.cursor.execute(sql_delete_pedido, (id_pedido,))

            self.db.connection.commit()

            if self.db.cursor.rowcount > 0:  # Refere-se ao DELETE FROM Pedidos
                print(
                    f"✅ Pedido (ID: {id_pedido}) e seus pratos associados deletados com sucesso."
                )
                return True
            else:
                print(f"⚠️ Pedido (ID: {id_pedido}) não encontrado para deleção.")
                return False
        except mysql.connector.Error as e:
            self.db.connection.rollback()
            print(f"❌ Erro ao deletar pedido (ID: {id_pedido}): \n{e}")
            return False
