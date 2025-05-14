from datetime import date
from tkinter import messagebox
import mysql
import mysql.connector

from src.database.connectFromDB import Database
from src.models.address import Address
from src.models.phones import Phones


class Collaborator:
    def __init__(self):
        self.db = Database()
        self.phones = Phones(self.db)
        self.address = Address(self.db)

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

            self.fk_telefone = self.phones.inserirTelefone(novo_numero=telefone)
            self.fk_endereco = self.address.inserirEndereco(endereco=endereco)
            self.db.abrirConexao()
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
        except mysql.connector.Error as e:
            self.phones.deletarTelefone(self.fk_telefone)
            self.address.deletarEndereco(self.fk_endereco)
            raise ValueError(f"❌ Erro ao inserir um novo colaborador: \n{e}")
        finally:
            self.db.fecharConexao()

    def atualizarColaborador(
        self,
        cpf: str,
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
            cpf (str): CPF atual do colaborador (identificador de busca).
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
            self.db.abrirConexao()
            valores_dict = {}
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

            if novo_telefone is not None:
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
                        tabela="enderecos",
                        valores_dict={"endereco": novo_endereco},
                        campo_where="id_endereco",
                        valor_where=id_endereco,
                    )
        except mysql.connector.Error as e:
            print(f"❌ ocorreu um erro ao atualizar o cliente: \a {e}")
        finally:
            self.db.fecharConexao()

    def deletarColaborador(self, cpf_colaborador: int):
        """
        Remove um colaborador do banco de dados com base no CPF.

        Args:
            cpf_colaborador (int): CPF do colaborador a ser removido.

        Raises:
            mysql.connector.Error: Se ocorrer erro durante a exclusão.
        """

        try:
            self.db.abrirConexao()
            sql = "DELETE FROM colaboradores WHERE cpf = %s"
            self.db.cursor.execute(sql, (cpf_colaborador,))
            self.db.connection.commit()
            print(f"✅ Colaborador com CPF:({cpf_colaborador}) excluído com sucesso.")
        except mysql.connector.Error as e:
            print(f"❌ Erro ao excluir o colaborador:\n{e}")
        finally:
            self.db.fecharConexao()

    def cpf_existe(self, cpf: str) -> bool:
        """
         Verifica se um CPF já está cadastrado no banco de dados.

        Args:
            cpf (str): CPF a ser verificado (com ou sem formatação)

        Returns:
            bool: True se o CPF existe, False se não existe ou em caso de erro

        Raises:
            ValueError: Se o CPF for inválido
        """
        try:
            self.db.abrirConexao()
            # Remove caracteres não numéricos e valida formato básico
            cpf_limpo = "".join(filter(str.isdigit, cpf))
            if len(cpf_limpo) != 11:
                raise ValueError("CPF deve conter 11 dígitos")

            # Consulta segura com parâmetros para evitar SQL injection
            sql = "SELECT COUNT(1) AS total FROM colaboradores WHERE cpf = %s"
            self.db.cursor.execute(sql, (cpf_limpo,))

            # Obtém o resultado (fetchone retorna uma tupla, ex: (1,))
            resultado = self.db.cursor.fetchone()

            # Retorna True se count > 0
            return resultado["total"] > 0 if resultado else False
        except Exception as e:
            raise ValueError(f"Erro ao verificar CPF: \a {str(e)}")
        except mysql.connector.Error as e:
            raise ValueError(f"Erro ao validar cpf: \a {e}")
        finally:
            self.db.fecharConexao()

    def recuperar_colaboradores(self) -> list:
        """Recupera todos os colaboradores da tabela 'colaboradores' no MySQL

        Returns:
            list: Lista de dicionários com os dados dos colaboradores
        """
        try:
            self.db.abrirConexao()
            # Executa a consulta SQL
            self.db.cursor.execute(
                """
            SELECT 
                cpf,
                nome,
                DATE_FORMAT(dataAd, '%d/%m/%Y') as data_admissao,
                nivelSistem,
                funcao,
                fk_telefone,
                fk_endereco
            FROM colaboradores
            ORDER BY nome
            """
            )

            # Obtém os resultados
            resultados = self.db.cursor.fetchall()

            return resultados

        except mysql.connector.Error as e:
            messagebox.showerror("Erro", f"Falha ao recuperar colaboradores: {str(e)}")
            return []
        finally:
            self.db.fecharConexao()

    def recuperar_colaboradores_completos(self) -> list:
        """Versão otimizada que reduz o número de consultas ao banco"""
        try:
            self.db.abrirConexao()
            # 1. Recupera todos os colaboradores
            colaboradores = self.recuperar_colaboradores()

            # 2. Coleta todos os IDs únicos de telefones e endereços
            telefones_ids = {
                c["fk_telefone"] for c in colaboradores if c.get("fk_telefone")
            }
            enderecos_ids = {
                c["fk_endereco"] for c in colaboradores if c.get("fk_endereco")
            }

            # 3. Busca todos os telefones e endereços de uma só vez
            telefones = {
                t["id_telefone"]: t
                for t in self.phones.buscar_telefone_por_id(list(telefones_ids))
            }
            enderecos = {
                e["id_endereco"]: e
                for e in self.address.buscar_endereco_por_id(list(enderecos_ids))
            }

            # 4. Combina os dados
            for colab in colaboradores:
                if colab.get("fk_telefone") and colab["fk_telefone"] in telefones:
                    colab.update(
                        {
                            "telefone_info": telefones[colab["fk_telefone"]][
                                "telefone"
                            ],
                            "telefone_id": colab["fk_telefone"],
                        }
                    )

                if colab.get("fk_endereco") and colab["fk_endereco"] in enderecos:
                    colab.update(
                        {
                            "endereco_info": enderecos[colab["fk_endereco"]][
                                "endereco"
                            ],
                            "endereco_id": colab["fk_endereco"],
                        }
                    )

            return colaboradores

        except Exception as e:
            print(f"Erro ao recuperar dados completos: {e}")
            return []
        except mysql.connector.Error as e:
            raise Exception(f"Erro ao recuperar dados completos: {e}")
        finally:
            self.db.fecharConexao()
