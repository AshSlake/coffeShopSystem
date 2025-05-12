import mysql.connector
from datetime import date
from enum import Enum
from dotenv import load_dotenv
import os

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()


class Database:
    def __init__(self):
        """Inicializa a conexão com o banco de dados MySQL."""
        self.connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
        )
        self.cursor = self.connection.cursor()

    # SISTEMA:
    def verificarConexao(self):
        """Verifica se a conexão com o banco de dados está ativa.

        Raises:
            mysql.connector.Error: Se houver erro ao verificar a conexão.
        """
        try:
            if self.connection.is_connected():
                print("✅ Conexao estabelecida com sucesso")
        except mysql.connector.Error as e:
            print(f"❌ Erro ao se conectar ao Banco de dados: \n {e}")

    def fecharConexao(self):
        """Fecha a conexão com o banco de dados.

        Raises:
            mysql.connector.Error: Se ocorrer erro ao fechar a conexão.
        """
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
            print("🔒 Conexão encerrada.")
        except mysql.connector.Error as e:
            print(f"❌ Erro ao fechar a conexão: {e}")

    # SESSÃO CLIENTE:
    def inserirCliente(
        self, cpf: int = None, nome: str = None, fk_telefone: int = None
    ):
        """Insere um novo cliente no banco de dados.

        Args:
            cpf (int): CPF do cliente.
            nome (str): Nome do cliente.
            fk_telefone (int): ID do telefone associado ao cliente.

        Raises:
            mysql.connector.Error: Se ocorrer um erro ao inserir o cliente.
        """
        try:
            sql = "INSERT INTO clientes (cpf, nome, fk_telefone) VALUES (%s,%s,%s)"
            data: tuple = (cpf, nome, fk_telefone)
            self.cursor.execute(sql, data)
            self.connection.commit()
            print(f"✅ {nome} foi adicionado com sucesso!")
        except mysql.connector.Error as e:
            print(f"❌ Erro ao inserir o novo cliente: \n {e}")

    def atualizarCliente(
        self,
        cpf: int,
        novo_cpf: int = None,
        novo_nome: str = None,
        novo_telefone: int = None,
    ):
        """Atualiza os dados de um cliente existente.

        Args:
            cpf (int): CPF atual do cliente.
            novo_cpf (int, optional): Novo CPF.
            novo_nome (str, optional): Novo nome.
            novo_telefone (int, optional): Novo número de telefone.

        Raises:
            mysql.connector.Error: Se ocorrer erro ao atualizar o cliente.
        """
        try:
            valores_dict = {}
            if novo_cpf is not None:
                valores_dict["cpf"] = novo_cpf
            if novo_nome is not None:
                valores_dict["nome"] = novo_nome

            if valores_dict:
                self.atualizarRegistro("clientes", valores_dict, "cpf", cpf)

            if novo_telefone is not None:
                id_telefone = self.buscarTelefoneCliente(cpf)
                if id_telefone is not None:
                    self.atualizarRegistro(
                        "telefones",
                        {"telefone": novo_telefone},
                        "id_telefone",
                        id_telefone,
                    )
        except (
            mysql.connector.Error
        ):  # Genérico, idealmente tratar especificamente ou relançar
            print("❌ ocorreu um erro ao atualizar o cliente.")

    def deletarCliente(self, cpf: int):
        """Deleta um cliente do banco de dados.

        Args:
            cpf (int): CPF do cliente a ser deletado.

        Raises:
            mysql.connector.Error: Se ocorrer erro ao deletar o cliente.
        """
        try:
            sql = "DELETE FROM clientes WHERE cpf = %s;"
            self.cursor.execute(sql, (cpf,))
            self.connection.commit()
            print("✅ Cliente deletado com sucesso.")
        except mysql.connector.Error as e:
            print(f"❌ Erro ao deletar o Cliente: \n {e}")

    # SESSÃO TELEFONE:
    def buscarTelefoneCliente(self, idClient: int):
        """Busca o ID do telefone associado a um cliente.

        Args:
            idClient (int): CPF do cliente.

        Returns:
            int | None: ID do telefone se encontrado, senão None.

        Raises:
            mysql.connector.Error: Se ocorrer erro na consulta.
        """
        try:
            sql = "SELECT fk_telefone FROM clientes WHERE cpf = %s"
            self.cursor.execute(sql, (idClient,))
            resultado = self.cursor.fetchone()
            return resultado[0] if resultado else None
        except mysql.connector.Error as e:
            print(f"❌ Erro ao buscar telefone do cliente: \n {e}")
            return None

    def inserirTelefone(self, novo_numero: int, cpf: int = None):
        """Insere um novo número de telefone.

        Args:
            novo_numero (int): Número de telefone.
            cpf (int, optional): CPF do cliente a associar (assumindo que a tabela telefones tem fk_cliente).

        Returns:
            int: ID do telefone recém-inserido.

        Raises:
            mysql.connector.Error: Se ocorrer erro ao inserir o telefone.
        """
        try:
            # Ajustado para um insert mais padrão, assumindo que 'fk_cliente' pode ser NULL
            # ou que você sempre fornecerá um CPF se for para associar.
            sql = "INSERT INTO telefones (telefone, fk_cliente) VALUES (%s, %s)"
            valores = (novo_numero, cpf)
            self.cursor.execute(sql, valores)
            self.connection.commit()
            newID = self.cursor.lastrowid
            print(f"✅ Telefone: {novo_numero} adicionado com sucesso!")
            return newID
        except mysql.connector.Error as e:
            print(f"❌ Erro ao inserir telefone: \n {e}")
            # Considere relançar o erro ou retornar None para indicar falha
            # raise

    def atualizarTelefone(
        self, id_telefone: int, novo_numero: int = None, fk_cliente: int = None
    ):
        """Atualiza os dados de um telefone existente.

        Args:
            id_telefone (int): ID do telefone.
            novo_numero (int, optional): Novo número.
            fk_cliente (int, optional): CPF do cliente a associar.

        Raises:
            mysql.connector.Error: Se ocorrer erro na atualização.
        """
        valores_dict = {}
        if novo_numero is not None:
            valores_dict["telefone"] = novo_numero
        if fk_cliente is not None:
            valores_dict["fk_cliente"] = fk_cliente

        if valores_dict:
            try:
                self.atualizarRegistro(
                    "telefones", valores_dict, "id_telefone", id_telefone
                )
            except (
                mysql.connector.Error
            ) as e:  # Adicionado para capturar erro do atualizarRegistro
                print(f"❌ Erro ao atualizar telefone: \n {e}")
                # raise

    def deletarTelefone(self, id_telefone):
        """Deleta um número de telefone.

        Args:
            id_telefone (int): ID do telefone.

        Raises:
            mysql.connector.Error: Se ocorrer erro na exclusão.
        """
        try:
            sql = "DELETE FROM telefones WHERE id_telefone = %s"
            self.cursor.execute(sql, (id_telefone,))
            self.connection.commit()
            print("✅ Número deletado com sucesso.")
        except mysql.connector.Error as e:
            print(f"❌ Erro ao deletar o telefone: {e}")

    # SESSÃO COLABORADOR:
    def inserirColaborador(
        self,
        cpf: int = None,
        nome: str = None,
        dataAd: date = None,
        nivelSystem: int = None,
        funcao: str = None,
        fk_telefone: int = None,
        fk_endereco: int = None,
    ):
        """
        Insere um novo colaborador no banco de dados.

        Args:
            cpf (int, optional): CPF do colaborador.
            nome (str, optional): Nome completo do colaborador.
            dataAd (date, optional): Data de admissão do colaborador.
            nivelSystem (int, optional): Nível de acesso do colaborador no sistema.
            funcao (str, optional): Função/cargo do colaborador.
            fk_telefone (int, optional): Chave estrangeira para a tabela de telefone.
            fk_endereco (int, optional): Chave estrangeira para a tabela de endereço.

        Returns:
            None

        Raises:
            mysql.connector.Error: Se ocorrer um erro ao executar a inserção no banco.
        """
        try:
            sql = """
            INSERT INTO colaboradores
            (cpf, nome, dataAd, nivelSistem, funcao, fk_telefone, fk_endereco)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            data: tuple = (
                cpf,
                nome,
                dataAd,
                nivelSystem,  # Corrigido para nivelSystem (como no parâmetro)
                funcao,
                fk_telefone,
                fk_endereco,
            )
            # A validação if all pode ser muito restritiva se alguns campos são opcionais (NULLable)
            # Considere delegar a validação de NOT NULL para o banco.
            # if all(item is not None for item in data):
            self.cursor.execute(sql, data)
            self.connection.commit()
            print("✅ Colaborador inserido com sucesso")
            # else:
            #     print("⚠️ Todos os campos precisam ser preenchidos para a inserção.")
            #     return
        except mysql.connector.Error as e:
            print(f"❌ Erro ao inserir um novo colaborador: \n{e}")

    # SESSÃO ENDEREÇO
    def inserirEndereco(self, endereco: str = None):
        """
        insere o endereço no banco de dados

        args:
            endereco(str): endereco do colaborador

        returns:
            newID(int): retorna o id do novo endereço inserido no banco de dados.

        raises:
            lança um mysql.connector.Error caso haja algum erro na inserção.
        """
        try:
            if endereco is not None:
                sql = "INSERT INTO enderecos(endereco) VALUES(%s);"
                data: tuple = (endereco,)
                self.cursor.execute(sql, data)
                self.connection.commit()
                newID = self.cursor.lastrowid
                print("✅ Endereco inserido com sucesso")
                return newID
            else:
                print("⚠️ Campo endereco foi fornecido vazio.")
                return None  # Retornar None para indicar falha ou ausência de inserção
        except mysql.connector.Error as e:
            print(f"❌ Erro ao inserir endereco na tabela: \n{e}")
            # raise

    # SESSÃO PREÇOS
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
            sql = "INSERT INTO Precos (preco) VALUES (%s)"
            self.cursor.execute(sql, (preco,))
            self.connection.commit()
            newID = self.cursor.lastrowid
            print(f"✅ Preço (ID: {newID}, Valor: {preco}) inserido com sucesso.")
            return newID
        except mysql.connector.Error as e:
            print(f"❌ Erro ao inserir preço: \n{e}")
            return None

    def atualizarPreco(self, id_preco: int, novo_preco: float):
        """
        Atualiza o valor de um preço existente.

        Args:
            id_preco (int): O ID do preço a ser atualizado.
            novo_preco (float): O novo valor do preço.

        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer um erro durante a atualização.
        """
        try:
            self.atualizarRegistro("Precos", {"preco": novo_preco}, "id", id_preco)
            return True
        except mysql.connector.Error as e:
            # O método atualizarRegistro já imprime o erro.
            # print(f"❌ Erro ao atualizar preço (ID: {id_preco}): \n{e}")
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
            sql = "DELETE FROM Precos WHERE id = %s"
            self.cursor.execute(sql, (id_preco,))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print(f"✅ Preço (ID: {id_preco}) deletado com sucesso.")
                return True
            else:
                print(f"⚠️ Preço (ID: {id_preco}) não encontrado para deleção.")
                return False
        except mysql.connector.Error as e:
            print(f"❌ Erro ao deletar preço (ID: {id_preco}): \n{e}")
            return False

    # SESSÃO INGREDIENTES
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
            self.cursor.execute(sql, (nome,))
            self.connection.commit()
            newID = self.cursor.lastrowid
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
            self.atualizarRegistro(
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
            self.cursor.execute(sql_remove_assoc, (id_ingrediente,))
            # Não precisa de commit aqui se o próximo comando for na mesma transação (auto-commit off)
            # Mas para garantir, vamos commitar se houver auto-commit ou fazer tudo em uma transação explícita.
            # self.connection.commit() # Depende da configuração de auto-commit

            sql = "DELETE FROM Ingredientes WHERE id = %s"
            self.cursor.execute(sql, (id_ingrediente,))
            self.connection.commit()  # Commit final
            if self.cursor.rowcount > 0:
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
            self.connection.rollback()  # Se algo deu errado, desfazer
            return False

    # SESSÃO PRATOS
    def inserirPrato(self, nome: str, fk_preco: int):
        """
        Insere um novo prato na tabela Pratos.

        Args:
            nome (str): O nome do prato.
            fk_preco (int): O ID do preço associado a este prato (da tabela Precos).

        Returns:
            int | None: O ID do prato recém-inserido, ou None em caso de falha.

        Raises:
            mysql.connector.Error: Se ocorrer um erro ao executar a inserção no banco.
        """
        try:
            sql = "INSERT INTO Pratos (nome, fk_preco) VALUES (%s, %s)"
            self.cursor.execute(sql, (nome, fk_preco))
            self.connection.commit()
            newID = self.cursor.lastrowid
            print(f"✅ Prato (ID: {newID}, Nome: {nome}) inserido com sucesso.")
            return newID
        except mysql.connector.Error as e:
            print(f"❌ Erro ao inserir prato: \n{e}")
            return None

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
            sql = "INSERT INTO Prato_Ingredientes (prato_id, ingrediente_id) VALUES (%s, %s)"
            self.cursor.execute(sql, (prato_id, ingrediente_id))
            self.connection.commit()
            print(
                f"✅ Ingrediente (ID: {ingrediente_id}) adicionado ao Prato (ID: {prato_id}) com sucesso."
            )
            return True
        except mysql.connector.Error as e:
            print(
                f"❌ Erro ao adicionar ingrediente (ID: {ingrediente_id}) ao Prato (ID: {prato_id}): \n{e}"
            )
            return False

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
            sql = "DELETE FROM Prato_Ingredientes WHERE prato_id = %s AND ingrediente_id = %s"
            self.cursor.execute(sql, (prato_id, ingrediente_id))
            self.connection.commit()
            if self.cursor.rowcount > 0:
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

    def atualizarPrato(
        self, id_prato: int, novo_nome: str = None, novo_fk_preco: int = None
    ):
        """
        Atualiza os dados de um prato existente.

        Args:
            id_prato (int): O ID do prato a ser atualizado.
            novo_nome (str, optional): O novo nome do prato.
            novo_fk_preco (int, optional): O novo ID do preço para o prato.

        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer um erro durante a atualização.
        """
        valores_dict = {}
        if novo_nome is not None:
            valores_dict["nome"] = novo_nome
        if novo_fk_preco is not None:
            valores_dict["fk_preco"] = novo_fk_preco

        if valores_dict:
            try:
                self.atualizarRegistro("Pratos", valores_dict, "id", id_prato)
                return True
            except mysql.connector.Error as e:
                return False
        else:
            print("⚠️ Nenhum campo fornecido para atualizar o prato.")
            return False

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
            self.connection.start_transaction()
            # Remover de tabelas de junção
            tabelas_juncao = ["Prato_Ingredientes", "Pedido_Pratos", "Cardapio_Pratos"]
            for tabela in tabelas_juncao:
                sql_remove_assoc = f"DELETE FROM {tabela} WHERE prato_id = %s"
                self.cursor.execute(sql_remove_assoc, (id_prato,))

            # Deletar o prato
            sql_delete_prato = "DELETE FROM Pratos WHERE id = %s"
            self.cursor.execute(sql_delete_prato, (id_prato,))

            self.connection.commit()

            # A verificação do rowcount aqui se refere apenas à última operação (DELETE FROM Pratos)
            if self.cursor.rowcount > 0:
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

    # SESSÃO PEDIDOS
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
            self.cursor.execute(sql, (num_mesa, fk_colaborador))
            self.connection.commit()
            newID = self.cursor.lastrowid
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
            self.cursor.execute(sql, (pedido_id, prato_id))
            self.connection.commit()
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
            self.cursor.execute(sql, (pedido_id, prato_id))
            self.connection.commit()
            if self.cursor.rowcount > 0:
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
                self.atualizarRegistro("Pedidos", valores_dict, "id_pedido", id_pedido)
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
            self.connection.start_transaction()
            # Remover de Pedido_Pratos primeiro
            sql_remove_assoc = "DELETE FROM Pedido_Pratos WHERE pedido_id = %s"
            self.cursor.execute(sql_remove_assoc, (id_pedido,))

            # Deletar o pedido
            sql_delete_pedido = "DELETE FROM Pedidos WHERE id_pedido = %s"
            self.cursor.execute(sql_delete_pedido, (id_pedido,))

            self.connection.commit()

            if self.cursor.rowcount > 0:  # Refere-se ao DELETE FROM Pedidos
                print(
                    f"✅ Pedido (ID: {id_pedido}) e seus pratos associados deletados com sucesso."
                )
                return True
            else:
                print(f"⚠️ Pedido (ID: {id_pedido}) não encontrado para deleção.")
                return False
        except mysql.connector.Error as e:
            self.connection.rollback()
            print(f"❌ Erro ao deletar pedido (ID: {id_pedido}): \n{e}")
            return False

    # SESSÃO CARDAPIO
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
            self.cursor.execute(sql)
            self.connection.commit()
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
            self.cursor.execute(sql, (cardapio_id, prato_id))
            self.connection.commit()
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
            self.cursor.execute(sql, (cardapio_id, prato_id))
            self.connection.commit()
            if self.cursor.rowcount > 0:
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
            self.connection.start_transaction()
            # Remover de Cardapio_Pratos primeiro
            sql_remove_assoc = "DELETE FROM Cardapio_Pratos WHERE cardapio_id = %s"
            self.cursor.execute(sql_remove_assoc, (id_cardapio,))

            # Deletar o cardápio
            sql_delete_cardapio = "DELETE FROM Cardapio WHERE id = %s"
            self.cursor.execute(sql_delete_cardapio, (id_cardapio,))

            self.connection.commit()

            if self.cursor.rowcount > 0:  # Refere-se ao DELETE FROM Cardapio
                print(
                    f"✅ Cardápio (ID: {id_cardapio}) e seus pratos associados deletados com sucesso."
                )
                return True
            else:
                print(f"⚠️ Cardápio (ID: {id_cardapio}) não encontrado para deleção.")
                return False
        except mysql.connector.Error as e:
            self.connection.rollback()
            print(f"❌ Erro ao deletar cardápio (ID: {id_cardapio}): \n{e}")
            return False

    # METODOS:
    def atualizarRegistro(
        self, tabela: str, valores_dict: dict, campo_where: str, valor_where
    ):
        """Atualiza registros de forma genérica em qualquer tabela.

        Args:
            tabela (str): Nome da tabela a ser atualizada.
            valores_dict (dict): Dicionário com campos e novos valores.
            campo_where (str): Campo da cláusula WHERE.
            valor_where (Any): Valor do campo da cláusula WHERE.

        Raises:
            mysql.connector.Error: Se ocorrer erro ao executar a atualização.
        """
        if not valores_dict:
            print("⚠️ Nenhum campo foi fornecido para atualização.")
            return  # Idealmente deveria retornar False ou levantar uma exceção

        try:
            campos_sql = [f"{campo} = %s" for campo in valores_dict.keys()]
            valores = list(valores_dict.values())
            valores.append(valor_where)

            sql = (
                f"UPDATE {tabela} SET {', '.join(campos_sql)} WHERE {campo_where} = %s"
            )
            self.cursor.execute(sql, tuple(valores))
            self.connection.commit()
            print(f"✅ Registro atualizado com sucesso na tabela '{tabela}'!")
        except mysql.connector.Error as e:
            print(f"❌ Erro ao atualizar registro na tabela '{tabela}':\n{e}")
            raise  # Relançar para que o chamador saiba do erro


# Exemplo de uso
if __name__ == "__main__":
    db = Database()
    db.verificarConexao()
    # --------------------------------------------------------------------------
    # # Exemplo Sessão Preços ✅
    # print("\n--- TESTANDO PREÇOS ---")
    # preco_id = db.inserirPreco(preco=10.99)
    # if preco_id:
    # db.atualizarPreco(id_preco=preco_id, novo_preco=12.50)
    # # db.deletarPreco(id_preco=preco_id)

    # # Exemplo Sessão Ingredientes
    # print("\n--- TESTANDO INGREDIENTES ---")
    # ingrediente_id = db.inserirIngrediente(nome="Tomate")
    # if ingrediente_id:
    #     db.atualizarIngrediente(
    #         id_ingrediente=ingrediente_id, novo_nome="Tomate Cereja"
    #     )
    #     # db.deletarIngrediente(id_ingrediente=ingrediente_id)
    # --------------------------------------------------------------------------
    # # Exemplo Sessão Pratos✅
    # print("\n--- TESTANDO PRATOS ---")
    # preco_para_prato_id = db.inserirPreco(preco=25.00)
    # ingrediente_para_prato_id = db.inserirIngrediente(nome="Queijo Mussarela")
    # if preco_para_prato_id and ingrediente_para_prato_id:
    #     prato_id = db.inserirPrato(
    #         nome="Pizza Margherita", fk_preco=preco_para_prato_id
    #     )
    #     if prato_id:
    #         db.adicionarIngredienteAoPrato(
    #             prato_id=prato_id, ingrediente_id=ingrediente_para_prato_id
    #         )
    #         db.adicionarIngredienteAoPrato(
    #             prato_id=prato_id, ingrediente_id=2
    #         )  # Reutilizando o tomate
    # db.atualizarPrato(id_prato=prato_id, novo_nome="Pizza Margherita Especial")
    # db.removerIngredienteDoPrato(prato_id=prato_id, ingrediente_id=ingrediente_para_prato_id)
    # db.deletarPrato(id_prato=prato_id) # Testar deleção
    # db.deletarIngrediente(ingrediente_para_prato_id) # Limpar
    # db.deletarPreco(preco_para_prato_id) # Limpar
    # --------------------------------------------------------------------------
    # print("\n--- TESTANDO PEDIDOS ---")✅
    # # Necessario ter um colaborador e um prato existentes
    # # id_colaborador_existente = # ... buscar ou inserir um colaborador
    # # id_prato_existente = prato_id # do exemplo anterior
    #
    # # Para testar, vamos inserir um colaborador caso não exista um
    # try:
    #     db.inserirColaborador(cpf=12345678900, nome="Garçom Teste", dataAd=date.today(), nivelSystem=NivelSistema.FUNCIONARIO.value, funcao=Cargos.FUNCIONARIO.value)
    # except mysql.connector.Error as e:
    #     if e.errno == 1062: # Duplicate entry
    #         print("Colaborador de teste já existe.")
    #     else:
    #         raise
    #
    # if prato_id: # Usando prato_id do teste anterior
    #     pedido_id = db.inserirPedido(num_mesa=5, fk_colaborador=12345678900)
    #     if pedido_id:
    #         db.adicionarPratoAoPedido(pedido_id=pedido_id, prato_id=prato_id)
    #         db.atualizarPedido(id_pedido=pedido_id, novo_num_mesa=10)
    #         db.removerPratoDoPedido(pedido_id=pedido_id, prato_id=prato_id)
    #         # db.deletarPedido(id_pedido=pedido_id) # Testar deleção

    # --------------------------------------------------------------------------
    # print("\n--- TESTANDO CARDÁPIO ---")✅
    # if prato_id: # Usando prato_id do teste anterior
    #     cardapio_id = db.criarCardapio()
    #     if cardapio_id:
    #         db.adicionarPratoAoCardapio(cardapio_id=cardapio_id, prato_id=prato_id)
    #         db.removerPratoDoCardapio(cardapio_id=cardapio_id, prato_id=prato_id)
    #         # db.deletarCardapio(id_cardapio=cardapio_id) # Testar deleção
    # --------------------------------------------------------------------------
    # Limpeza final dos exemplos✅
    # if "prato_id" in locals() and prato_id:
    #     db.deletarPrato(prato_id)
    # if "ingrediente_id" in locals() and ingrediente_id:
    #     db.deletarIngrediente(ingrediente_id)
    # if "preco_id" in locals() and preco_id:
    #     db.deletarPreco(preco_id)

    db.fecharConexao()
