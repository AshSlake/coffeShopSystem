# SESSÃO CLIENTE:
import mysql
import mysql.connector
from Phones import Phones
from ConnectFromDB import Database


class Customers:
    def __init__(self, db: Database, phone: Phones):
        self.db = db
        self.phones = phone

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
                self.db.atualizarRegistro("clientes", valores_dict, "cpf", cpf)

            if novo_telefone is not None:
                id_telefone = self.db.searchIDFromDataBase(
                    cpf, coluna="fk_telefone", tabela="clientes"
                )
                if id_telefone is not None:
                    self.db.atualizarRegistro(
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
            self.db.cursor.execute(sql, (cpf,))
            self.db.connection.commit()
            print("✅ Cliente deletado com sucesso.")
        except mysql.connector.Error as e:
            print(f"❌ Erro ao deletar o Cliente: \n {e}")
