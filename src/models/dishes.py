# SESSÃO PRATOS
import mysql, mysql.connector

from src.database.connectFromDB import Database
from src.models.prices import Prices


class Dishes:
    def __init__(self, db: Database):
        self.db = db
        self.price = Prices(self.db)

    def inserirPrato(self, nome: str, preco: float):
        """
        Insere um novo prato na tabela Pratos.

        Args:
            nome (str): O nome do prato.
            preco(int): preco a ser inserido no banco de dados

        Returns:
            int | None: O ID do prato recém-inserido, ou None em caso de falha.

        Raises:
            mysql.connector.Error: Se ocorrer um erro ao executar a inserção no banco.
        """
        try:
            fk_preco = self.price.inserirPreco(preco)
            self.db.abrirConexao()
            sql = "INSERT INTO Pratos (nome, fk_preco) VALUES (%s, %s)"
            self.db.cursor.execute(sql, (nome, fk_preco))
            self.db.connection.commit()
            newID = self.db.cursor.lastrowid
            print(f"✅ Prato (ID: {newID}, Nome: {nome}) inserido com sucesso.")
            return newID
        except mysql.connector.Error as e:
            print(f"❌ Erro ao inserir prato: \n{e}")
            return None
        finally:
            self.db.fecharConexao()

    def adicionarIngredienteAoPrato(self, prato_id: int, ingrediente_id: int):
        """
        Associa um ingrediente a um prato na tabela Prato_Ingredientes.

        Args:
            prato_id (int): O ID do prato.
            ingrediente_id (int): O ID do ingrediente.

        Returns:
            bool: True se a associação foi bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer um erro durante a inserção na tabela de junção.
        """
        try:
            self.db.abrirConexao()
            sql = "INSERT INTO Prato_Ingredientes (prato_id, ingrediente_id) VALUES (%s, %s)"
            self.db.cursor.execute(sql, (prato_id, ingrediente_id))
            self.db.connection.commit()
            print(
                f"✅ Ingrediente (ID: {ingrediente_id}) adicionado ao Prato (ID: {prato_id}) com sucesso."
            )
            return True
        except mysql.connector.Error as e:
            print(
                f"❌ Erro ao adicionar ingrediente (ID: {ingrediente_id}) ao Prato (ID: {prato_id}): \n{e}"
            )
            return False
        finally:
            self.db.fecharConexao()

    def removerIngredienteDoPrato(self, prato_id: int, ingrediente_id: int):
        """
        Remove a associação de um ingrediente a um prato da tabela Prato_Ingredientes.

        Args:
            prato_id (int): O ID do prato.
            ingrediente_id (int): O ID do ingrediente.

        Returns:
            bool: True se a remoção foi bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer um erro durante a deleção na tabela de junção.
        """
        try:
            self.db.abrirConexao()
            sql = "DELETE FROM Prato_Ingredientes WHERE prato_id = %s AND ingrediente_id = %s"
            self.db.cursor.execute(sql, (prato_id, ingrediente_id))
            self.db.connection.commit()
            if self.db.cursor.rowcount > 0:
                print(
                    f"✅ Ingrediente (ID: {ingrediente_id}) removido do Prato (ID: {prato_id}) com sucesso."
                )
                return True
            else:
                print(
                    f"⚠️ Associação não encontrada para remover Ingrediente (ID: {ingrediente_id}) do Prato (ID: {prato_id})."
                )
                return False
        except mysql.connector.Error as e:
            print(
                f"❌ Erro ao remover ingrediente (ID: {ingrediente_id}) do Prato (ID: {prato_id}): \n{e}"
            )
            return False
        finally:
            self.db.fecharConexao()

    def atualizarPrato(
        self, id_prato: int, novo_nome: str = None, novo_preco: float = None
    ):
        """
        Atualiza os dados de um prato existente.

        Args:
            id_prato (int): O ID do prato a ser atualizado.
            novo_nome (str, optional): O novo nome do prato.
            novo_preco (float, optional): O novo preço para o prato.

        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer um erro durante a atualização.
        """
        try:

            fk_preco = self.get_fk_preco_by_prato_id(id_prato)
            self.price.atualizarPreco(fk_preco, novo_preco)
            self.db.abrirConexao()
            valores_dict = {}
            if novo_nome is not None:
                valores_dict["nome"] = novo_nome

            if valores_dict:
                try:
                    self.db.atualizarRegistro("Pratos", valores_dict, "id", id_prato)
                    return True
                except mysql.connector.Error as e:
                    return False
            else:
                print("⚠️ Nenhum campo fornecido para atualizar o prato.")
                return False
        except mysql.connector.Error:
            return
        finally:
            self.db.fecharConexao()

    def deletarPrato(self, id_prato: int):
        """
        Deleta um prato da tabela Pratos e suas associações.
        Isso removerá o prato de Prato_Ingredientes, Pedido_Pratos e Cardapio_Pratos primeiro.

        Args:
            id_prato (int): O ID do prato a ser deletado.

        Returns:
            bool: True se a deleção foi bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer um erro durante a deleção.
        """
        try:
            self.db.abrirConexao()
            # Remover de tabelas de junção
            tabelas_juncao = ["Prato_Ingredientes", "Pedido_Pratos", "Cardapio_Pratos"]
            for tabela in tabelas_juncao:
                sql_remove_assoc = f"DELETE FROM {tabela} WHERE prato_id = %s"
                self.db.cursor.execute(sql_remove_assoc, (id_prato,))

            # Deletar o prato
            sql_delete_prato = "DELETE FROM Pratos WHERE id = %s"
            self.db.cursor.execute(sql_delete_prato, (id_prato,))

            self.db.connection.commit()

            # A verificação do rowcount aqui se refere apenas à última operação (DELETE FROM Pratos)
            if self.db.cursor.rowcount > 0:
                print(
                    f"✅ Prato (ID: {id_prato}) e suas associações deletados com sucesso."
                )
                return True
            else:
                # Isso pode acontecer se o prato já foi deletado ou não existia, mas as associações podem ter sido limpas.
                print(
                    f"⚠️ Prato (ID: {id_prato}) não encontrado para deleção (ou já deletado). Associações limpas se existiam."
                )
                return False  # Ou True se considerar a limpeza das associações um sucesso parcial.
        except mysql.connector.Error as e:
            self.connection.rollback()
            print(f"❌ Erro ao deletar prato (ID: {id_prato}): \n{e}")
            return False
        finally:
            self.db.fecharConexao()

    def recuperar_pratos_completos(self) -> list:
        """
        Recupera todos os pratos com nome, preço e ingredientes agregados.

        Returns:
            list: Lista de dicionários contendo os dados dos pratos e seus ingredientes.
        """
        try:
            self.db.abrirConexao()

            sql = """
            SELECT
                p.id,
                p.nome,
                pr.preco AS preco,
                GROUP_CONCAT(i.nome ORDER BY i.nome SEPARATOR ', ') AS ingredientes
            FROM pratos p
            JOIN precos pr ON pr.id = p.fk_preco
            LEFT JOIN Prato_Ingredientes pi ON pi.prato_id = p.id
            LEFT JOIN ingredientes i ON i.id = pi.ingrediente_id
            GROUP BY p.id, p.nome, pr.preco
            ORDER BY p.nome;
            """

            self.db.cursor.execute(sql)
            resultados = self.db.cursor.fetchall()

            return resultados

        except mysql.connector.Error as e:
            print(f"❌ Erro ao recuperar pratos completos:\n{e}")
            return []
        finally:
            self.db.fecharConexao()

    def recuperar_ingredientes(self) -> list:
        """
        Recupera todos os ingredientes da tabela Ingredientes.

        Returns:
            list: Lista de dicionários com id e nome de cada ingrediente.
        """
        try:
            self.db.abrirConexao()
            self.db.cursor.execute("SELECT id, nome FROM Ingredientes ORDER BY nome")
            return self.db.cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"❌ Erro ao recuperar ingredientes:\n{e}")
            return []
        finally:
            self.db.fecharConexao()

    def get_fk_preco_by_prato_id(self, prato_id: int) -> int | None:
        """
        Retorna o fk_preco (id da tabela Precos) para o dado prato_id.
        """
        try:
            self.db.abrirConexao()
            sql = "SELECT fk_preco FROM Pratos WHERE id = %s"
            self.db.cursor.execute(sql, (prato_id,))
            row = self.db.cursor.fetchone()
            if not row:
                return None
            # Se o cursor estiver em dictionary=True:
            return row["fk_preco"]
            # Se não for em dict mode, row[0]
        finally:
            self.db.fecharConexao()
