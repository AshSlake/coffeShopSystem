import mysql

from src.database.connectFromDB import Database


class Phones:
    def __init__(self, db: Database):
        self.db = db

    def inserirTelefone(self, novo_numero: int):
        """Insere um novo número de telefone.

        Args:
            novo_numero (int): Número de telefone.
        Returns:
            int: ID do telefone recém-inserido.

        Raises:
            mysql.connector.Error: Se ocorrer erro ao inserir o telefone.
        """
        try:
            # Ajustado para um insert mais padrão, assumindo que 'fk_cliente' pode ser NULL
            # ou que você sempre fornecerá um CPF se for para associar.
            sql = "INSERT INTO telefones (telefone) VALUES (%s)"
            valores = (novo_numero,)
            self.db.cursor.execute(sql, valores)
            self.db.connection.commit()
            newID = self.db.cursor.lastrowid
            print(f"✅ Telefone: {novo_numero} adicionado com sucesso!")
            return newID
        except mysql.connector.Error as e:
            print(f"❌ Erro ao inserir telefone: \n {e}")
            # Considere relançar o erro ou retornar None para indicar falha
            # raise

    def atualizarTelefone(
        self, id_telefone: int, novo_numero: int = None, fk_cliente: str = None
    ):
        """Atualiza os dados de um telefone existente.

        Args:
            id_telefone (int): ID do telefone.
            novo_numero (int, optional): Novo número.
            fk_cliente (str, optional): CPF do cliente a associar.

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
                self.db.atualizarRegistro(
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
            self.db.cursor.execute(sql, (id_telefone,))
            self.db.connection.commit()
            print("✅ Número deletado com sucesso.")
        except mysql.connector.Error as e:
            print(f"❌ Erro ao deletar o telefone: \n {e}")
