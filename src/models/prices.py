# SESSÃO PREÇOS
import mysql, mysql.connector

from src.database.connectFromDB import Database


class Prices:
    def __init__(self, db: Database):
        self.db = db

    def inserirPreco(self, preco: float):
        """
        Insere um novo preço na tabela Precos.

        Args:
            preco (float): O valor do preço a ser inserido.

        Returns:
            int | None: O ID do preço recém-inserido, ou None em caso de falha.

        Raises:
            mysql.connector.Error: Se ocorrer um erro ao executar a inserção no banco.
        """
        try:
            self.db.abrirConexao()
            sql = "INSERT INTO Precos (preco) VALUES (%s)"
            self.db.cursor.execute(sql, (preco,))
            self.db.connection.commit()
            newID = self.db.cursor.lastrowid
            print(f"✅ Preço (ID: {newID}, Valor: {preco}) inserido com sucesso.")
            return newID
        except mysql.connector.Error as e:
            print(f"❌ Erro ao inserir preço: \n{e}")
            return None
        finally:
            self.db.fecharConexao()

    def atualizarPreco(self, id_preco, novo_preco):
        """
        Atualiza o valor de um preço na tabela Precos.
        """
        try:
            # 🔒 Corrige se estiver vindo como lista
            if isinstance(novo_preco, list):
                novo_preco = novo_preco[0]
            if isinstance(id_preco, list):
                id_preco = id_preco[0]

            valores_dict = {"preco": float(novo_preco)}
            self.db.atualizarRegistro("Precos", valores_dict, "id", id_preco)
            return True
        except mysql.connector.Error as e:
            print(f"❌ Erro ao atualizar preço (ID: {id_preco}): \n{e}")
            return False

    def deletarPreco(self, id_preco: int):
        """
        Deleta um preço da tabela Precos.
        Atenção: Se este preço estiver sendo usado por algum prato,
        a deleção pode falhar a menos que ON DELETE CASCADE esteja configurado
        ou o prato seja atualizado/deletado primeiro.

        Args:
            id_preco (int): O ID do preço a ser deletado.

        Returns:
            bool: True se a deleção foi bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer um erro durante a deleção.
        """
        try:
            self.db.abrirConexao()
            sql = "DELETE FROM Precos WHERE id = %s"
            self.db.cursor.execute(sql, (id_preco,))
            self.db.connection.commit()
            if self.db.cursor.rowcount > 0:
                print(f"✅ Preço (ID: {id_preco}) deletado com sucesso.")
                return True
            else:
                print(f"⚠️ Preço (ID: {id_preco}) não encontrado para deleção.")
                return False
        except mysql.connector.Error as e:
            print(f"❌ Erro ao deletar preço (ID: {id_preco}): \n{e}")
            return False
        finally:
            self.db.fecharConexao()
