# SESSÃO CLIENTE:
from tkinter import messagebox
import mysql
import mysql.connector

from src.database.connectFromDB import Database
from src.models.phones import Phones


class Customers:
    def __init__(self, db: Database, phone: Phones):
        self.db = db
        self.phones = phone

    def inserirCliente(self, cpf: str = None, nome: str = None, telefone: int = None):
        """Insere um novo cliente no banco de dados.

        Args:
            cpf (str): CPF do cliente.
            nome (str): Nome do cliente.
            fk_telefone (int): ID do telefone associado ao cliente.

        Raises:
            mysql.connector.Error: Se ocorrer um erro ao inserir o cliente.
        """
        try:
            fk_telefone = self.phones.inserirTelefone(telefone)
            self.db.abrirConexao()
            sql = "INSERT INTO clientes (cpf, nome, fk_telefone) VALUES (%s,%s,%s)"
            data: tuple = (cpf, nome, fk_telefone)
            self.db.cursor.execute(sql, data)
            self.db.connection.commit()
            print(f"✅ {nome} foi adicionado com sucesso!")
        except mysql.connector.Error as e:
            print(f"❌ Erro ao inserir o novo cliente: \n {e}")
        finally:
            self.db.fecharConexao()

    def atualizarCliente(
        self,
        cpf: int,
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
            self.db.abrirConexao()
            valores_dict = {}
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
        finally:
            self.db.fecharConexao()

    def deletarCliente(self, cpf: int):
        """Deleta um cliente do banco de dados.

        Args:
            cpf (int): CPF do cliente a ser deletado.

        Raises:
            mysql.connector.Error: Se ocorrer erro ao deletar o cliente.
        """
        try:
            self.db.abrirConexao()
            sql = "DELETE FROM clientes WHERE cpf = %s;"
            self.db.cursor.execute(sql, (cpf,))
            self.db.connection.commit()
            print("✅ Cliente deletado com sucesso.")
        except mysql.connector.Error as e:
            print(f"❌ Erro ao deletar o Cliente: \n {e}")
        finally:
            self.db.fecharConexao()

    def recuperar_clientes(self) -> list:
        """Recupera todos os clientes da tabela 'clientes' no MySQL

        Returns:
            list: Lista de dicionários com os dados dos clientes
        """
        try:
            self.db.abrirConexao()
            self.db.cursor.execute(
                """
            SELECT 
                cpf,
                nome,
                fk_telefone
            FROM clientes
            ORDER BY nome
            """
            )
            resultados = self.db.cursor.fetchall()
            return resultados

        except mysql.connector.Error as e:
            messagebox.showerror("Erro", f"Falha ao recuperar clientes: {str(e)}")
            return []
        finally:
            self.db.fecharConexao()

    def recuperar_clientes_completos(self) -> list:
        """Recupera os dados de clientes com informações de telefone."""
        try:
            self.db.abrirConexao()

            # 1. Recupera todos os clientes
            clientes = self.recuperar_clientes()

            # 2. Coleta todos os IDs únicos de telefones
            telefones_ids = {c["fk_telefone"] for c in clientes if c.get("fk_telefone")}

            # 3. Busca todos os telefones de uma só vez
            telefones = {
                t["id_telefone"]: t
                for t in self.phones.buscar_telefone_por_id(list(telefones_ids))
            }

            # 4. Combina os dados
            for cliente in clientes:
                if cliente.get("fk_telefone") and cliente["fk_telefone"] in telefones:
                    cliente.update(
                        {
                            "telefone_info": telefones[cliente["fk_telefone"]][
                                "telefone"
                            ],
                            "telefone_id": cliente["fk_telefone"],
                        }
                    )

            return clientes

        except Exception as e:
            print(f"Erro ao recuperar dados completos dos clientes: {e}")
            return []
        except mysql.connector.Error as e:
            raise Exception(f"Erro ao recuperar dados completos dos clientes: {e}")
        finally:
            self.db.fecharConexao()

    def cpf_existe_cliente(self, cpf: str) -> bool:
        """
        Verifica se um CPF já está cadastrado na tabela 'clientes'.

        Args:
            cpf (str): CPF a ser verificado (com ou sem formatação)

        Returns:
            bool: True se o CPF existe, False se não existe ou em caso de erro

        Raises:
            ValueError: Se o CPF for inválido
        """
        try:
            self.db.abrirConexao()

            # Remove caracteres não numéricos
            cpf_limpo = "".join(filter(str.isdigit, cpf))
            if len(cpf_limpo) != 11:
                raise ValueError("CPF deve conter 11 dígitos")

            # Consulta na tabela 'clientes'
            sql = "SELECT COUNT(1) AS total FROM clientes WHERE cpf = %s"
            self.db.cursor.execute(sql, (cpf_limpo,))
            resultado = self.db.cursor.fetchone()

            return resultado["total"] > 0 if resultado else False

        except Exception as e:
            raise ValueError(f"Erro ao verificar CPF: \n{str(e)}")
        except mysql.connector.Error as e:
            raise ValueError(f"Erro ao validar CPF: \n{e}")
        finally:
            self.db.fecharConexao()
