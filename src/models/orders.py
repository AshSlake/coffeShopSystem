# SESSÃO PEDIDOS
import mysql, mysql.connector

from src.database.connectFromDB import Database


class Orders:
    def __init__(self, db: Database):
        self.db = db

    def inserirPedido(
        self,
        num_mesa: int,
        fk_colaborador: int,
        status,
        pratos: list = None,
    ):
        """
        Insere um novo pedido na tabela Pedidos.

        Args:
            num_mesa (int): O número da mesa para o pedido.
            fk_colaborador (int): O CPF do colaborador que registrou o pedido.
            status(str): status do pedido a ser adicionado inicialmente definido como pendente.
            pratos(list): lista com os ids para adição no banco de dados

        Returns:
            int | None: O ID do pedido recém-inserido, ou None em caso de falha.

        Raises:
            mysql.connector.Error: Se ocorrer um erro ao executar a inserção no banco.
        """
        try:
            # Criação do pedido
            self.db.abrirConexao()
            sql = "INSERT INTO Pedidos (numMesa, fk_colaborador,status_pedido) VALUES (%s, %s, %s)"
            self.db.cursor.execute(sql, (num_mesa, fk_colaborador, status))
            self.db.connection.commit()
            newID = self.db.cursor.lastrowid
            print(f"✅ Pedido (ID: {newID}) para mesa {num_mesa} inserido com sucesso.")
            # ----------------------------------------------------------------------------
            # Adicionar pratos ao pedido
            try:
                for prato_id in pratos:
                    self.adicionarPratoAoPedido(newID, prato_id)
                    print(
                        f"✅ Prato (ID: {prato_id}) adicionado ao pedido {newID} com sucesso."
                    )
            except mysql.connector.Error as e:
                raise RuntimeError(f"Falha na inserção do pedido: {e.msg}") from e

            return newID
        except mysql.connector.Error as e:
            raise RuntimeError(f"Falha na inserção do pedido: {e.msg}") from e
        finally:
            self.db.fecharConexao()

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
            self.db.abrirConexao()
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
        finally:
            self.db.fecharConexao()

    def atualizarPedido(
        self,
        id_pedido: int,
        novo_num_mesa: int = None,
        novo_fk_colaborador: int = None,
        novo_status: str = None,
        novos_pratos: list = None,
    ):
        """
        Atualiza os dados de um pedido existente.

        Args:
            id_pedido (int): O ID do pedido a ser atualizado.
            novo_num_mesa (int, optional): O novo número da mesa.
            novo_fk_colaborador (int, optional): O novo CPF do colaborador.
            novo_status(str): novo status do pedido.

        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer um erro durante a atualização.
        """
        try:
            # Atualiza dados do pedido, se houver campos
            valores_dict = {}
            if novo_num_mesa is not None:
                valores_dict["numMesa"] = novo_num_mesa
            if novo_fk_colaborador is not None:
                valores_dict["fk_colaborador"] = novo_fk_colaborador
            if novo_status is not None:
                valores_dict["status_pedido"] = novo_status

            if valores_dict:
                self.db.atualizarRegistro(
                    "pedidos", valores_dict, "id_pedido", id_pedido
                )
                print(f"✅ Pedido {id_pedido} atualizado com sucesso.")

            # Adiciona novos pratos, se houver
            if novos_pratos:
                for prato_id in novos_pratos:
                    self.adicionarPratoAoPedido(id_pedido, prato_id)
                    print(
                        f"✅ Prato (ID: {prato_id}) adicionado ao pedido {id_pedido}."
                    )

            # Retorna True se pelo menos uma ação foi feita
            if valores_dict or novos_pratos:
                return True
            else:
                print("⚠️ Nenhum dado fornecido para atualizar ou adicionar.")
                return False

        except mysql.connector.Error as e:
            raise RuntimeError(f"Erro ao atualizar o pedido: {e.msg}") from e

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
            self.db.abrirConexao()
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
        finally:
            self.db.fecharConexao()

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
            self.db.abrirConexao()
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
        finally:
            self.db.fecharConexao()

    def recuperar_pedidos(self) -> dict:
        """Obtém todos os pedidos do sistema com seus pratos e ingredientes associados.

        Realiza uma consulta no banco de dados que relaciona as tabelas:
        - Pedidos
        - Colaboradores
        - Pedido_Pratos
        - Pratos
        - Prato_Ingredientes
        - Ingredientes

        Returns:
            dict or None: Um dicionário estruturado contendo todos os pedidos agrupados por ID, onde cada pedido contém:
                - numero_da_mesa (int): Número da mesa do pedido
                - nome_do_colaborador (str): Nome do colaborador que registrou o pedido
                - status_pedido(str) : status atual do pedido
                - pratos (list): Lista de dicionários contendo:
                    - prato (str): Nome do prato
                    - ingredientes (list): Lista de nomes de ingredientes do prato
            Retorna None caso ocorra algum erro na conexão com o banco de dados.

        Raises:
            mysql.connector.Error: Exceção original do MySQL Connector (capturada internamente)
        """
        try:
            self.db.abrirConexao()
            sql = """
             SELECT
                p.id_pedido,
                p.numMesa AS 'numero_da_mesa',
                c.nome AS 'nome_do_colaborador',
                p.status_pedido,
                pr.nome AS 'prato',
                GROUP_CONCAT(DISTINCT i.nome SEPARATOR ', ') AS 'ingredientes'
            FROM Pedidos p
            INNER JOIN Colaboradores c ON p.fk_colaborador = c.cpf
            INNER JOIN Pedido_Pratos pp ON p.id_pedido = pp.pedido_id
            INNER JOIN Pratos pr ON pp.prato_id = pr.id
            INNER JOIN Prato_Ingredientes pi ON pr.id = pi.prato_id
            INNER JOIN Ingredientes i ON pi.ingrediente_id = i.id
            GROUP BY p.id_pedido, p.numMesa, c.nome, p.status_pedido, pr.nome
            ORDER BY p.id_pedido;
            """
            self.db.cursor.execute(sql)
            resultado = self.db.cursor.fetchall()

            # Formata os resultados para melhor visualização
            pedidos_agrupados = {}
            for row in resultado:
                pedido_id = row["id_pedido"]
                if pedido_id not in pedidos_agrupados:
                    pedidos_agrupados[pedido_id] = {
                        "numero_da_mesa": row["numero_da_mesa"],
                        "nome_do_colaborador": row["nome_do_colaborador"],
                        "status_pedido": row["status_pedido"],
                        "pratos": [],
                    }

                pedidos_agrupados[pedido_id]["pratos"].append(
                    {
                        "prato": row["prato"],
                        "ingredientes": (
                            row["ingredientes"].split(", ")
                            if row["ingredientes"]
                            else []
                        ),
                    }
                )

            return pedidos_agrupados
        except mysql.connector.Error as e:
            print(f"❌ Erro ao recuperar último cardápio completo: \n{e}")
            return {"id": None, "pratos": []}
        finally:
            self.db.fecharConexao()
