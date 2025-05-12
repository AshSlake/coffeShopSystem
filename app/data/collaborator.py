from datetime import date
import mysql
import mysql.connector
from Phones import Phones
from ConnectFromDB import Database
from Address import Address
from app.enums.Enums import Cargos, NivelSistema


class Customers:
    def __init__(self, db: Database, phone: Phones, address: Address):
        self.db = db
        self.phones = phone
        self.address = address

    def inserirColaborador(
        self,
        cpf: int = None,
        nome: str = None,
        dataAd: date = None,
        nivelSystem: int = None,
        funcao: str = None,
        telefone: int = None,
        endereco: str = None,
    ):
        """
        Insere um novo colaborador no banco de dados.

        Args:
            cpf (int, optional): CPF do colaborador.
            nome (str, optional): Nome completo do colaborador.
            dataAd (date, optional): Data de admissão do colaborador.
            nivelSystem (int, optional): Nível de acesso do colaborador no sistema.
            funcao (str, optional): Função/cargo do colaborador.
            telefone(int,optional): telefone do colaborador a ser salvo.
            endereco(srt,optional): endereço do colaborador.

        Returns:
            retorna o id do endereço e do telefone caso sejam cadastrados.

        Raises:
            mysql.connector.Error: Se ocorrer um erro ao executar a inserção no banco.
        """
        self.fk_telefone: int = None
        self.fk_endereco: str = None
        try:
            self.fk_telefone = self.phones.inserirTelefone(
                novo_numero=telefone, cpf=cpf
            )
            self.fk_endereco = self.address.inserirEndereco(endereco=endereco)
            sql = """
            INSERT INTO colaboradores
            (cpf, nome, dataAd, nivelSistem, funcao, fk_telefone, fk_endereco)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            data: tuple = (
                cpf,
                nome,
                dataAd,
                nivelSystem,
                funcao,
                self.fk_telefone,
                self.fk_endereco,
            )
            self.db.cursor.execute(sql, data)
            self.db.connection.commit()
            print("✅ Colaborador inserido com sucesso")
            # else:
            #     print("⚠️ Todos os campos precisam ser preenchidos para a inserção.")
            #     return
        except mysql.connector.Error as e:
            print(f"❌ Erro ao inserir um novo colaborador: \n{e}")

    def atualizarColaborador(
        self,
        cpf: int,
        novo_cpf: int,
        novo_nome: str = None,
        nova_data_AD: date = None,
        novo_nivel_system: str = None,
        nova_funcao: str = None,
        novo_telefone: int = None,
        novo_endereco: str = None,
    ):
        """Atualiza os dados de um colaborador existente no banco de dados.

        Este método permite atualizar um ou mais campos de um colaborador,
        incluindo CPF, nome, data de admissão, nível no sistema, função,
        telefone e endereço.

        Args:
            cpf (int): CPF atual do colaborador (identificador de busca).
            novo_cpf (int): Novo CPF a ser atribuído.
            novo_nome (str, opcional): Novo nome do colaborador.
            nova_data_AD (date, opcional): Nova data de admissão.
            novo_nivel_system (str, opcional): Novo nível no sistema.
            nova_funcao (str, opcional): Nova função do colaborador.
            novo_telefone (int, opcional): Novo número de telefone.
            novo_endereco (str, opcional): Novo endereço.

        Raises:
            mysql.connector.Error: Se ocorrer algum erro durante a atualização
            no banco de dados.
        """
        try:
            valores_dict = {}
            if novo_cpf is not None:
                valores_dict["cpf"] = novo_cpf
            if novo_nome is not None:
                valores_dict["nome"] = novo_nome
            if nova_data_AD is not None:
                valores_dict["dataAd"] = nova_data_AD
            if novo_nivel_system is not None:
                valores_dict["nivelSistem"] = novo_nivel_system
            if nova_funcao is not None:
                valores_dict["funcao"] = nova_funcao

            if valores_dict:
                set_clause = ", ".join(f"{key} = %s" for key in valores_dict.keys())
                sql = f"UPDATE colaboradores SET {set_clause} WHERE cpf = %s"
                values = list(valores_dict.values()) + [cpf]
                self.db.cursor.execute(sql, values)
                self.db.connection.commit()

            if novo_telefone or novo_endereco is not None:
                id_telefone_customer = self.db.searchIDFromDataBase(
                    cpf, coluna="fk_telefone", tabela="colaboradores"
                )
                if id_telefone_customer is not None:
                    self.db.atualizarRegistro(
                        "telefones",
                        {"telefone": novo_telefone},
                        "id_telefone",
                        id_telefone_customer,
                    )
            if novo_endereco is not None:
                id_endereco = self.db.searchIDFromDataBase(
                    cpf, coluna="fk_endereco", tabela="colaboradores"
                )
                if id_endereco is not None:
                    self.db.atualizarRegistro(
                        "enderecos",
                        {"endereco": novo_endereco},
                        "endereco",
                        id_endereco,
                    )
        except (
            mysql.connector.Error
        ):  # Genérico, idealmente tratar especificamente ou relançar
            print("❌ ocorreu um erro ao atualizar o cliente.")

    def deletarColaborador(self, cpf_colaborador: int):
        """
        Remove um colaborador do banco de dados com base no CPF.

        Args:
            cpf_colaborador (int): CPF do colaborador a ser removido.

        Raises:
            mysql.connector.Error: Se ocorrer erro durante a exclusão.
        """

        try:
            sql = "DELETE FROM colaboradores WHERE cpf = %s"
            self.db.cursor.execute(sql, (cpf_colaborador,))
            self.db.connection.commit()
            print(f"✅ Colaborador com CPF:({cpf_colaborador}) excluído com sucesso.")
        except mysql.connector.Error as e:
            print(f"❌ Erro ao excluir o colaborador:\n{e}")
