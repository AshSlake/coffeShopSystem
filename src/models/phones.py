import mysql

from src.database.connectFromDB import Database


class Phones:
    def __init__(self, db: Database):
        self.db = db

    def inserirTelefone(self, novo_numero: str):
        """Insere um novo número de telefone.

        Args:
            novo_numero (str): Número de telefone.
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

    def buscar_telefone_por_id(
        self, ids_telefone: int | list[int]
    ) -> dict | list[dict]:
        """
        Busca telefone(s) pelo(s) ID(s) na tabela 'telefones'.

        Este método aceita tanto um único ID quanto uma lista de IDs.
        Se for passado um único ID, retorna um único dicionário.
        Se for passada uma lista de IDs, retorna uma lista de dicionários.

        Args:
            ids_telefone (int | list[int]): ID único ou lista de IDs de telefones a serem buscados.

        Returns:
            dict | list[dict]:
                - Um dicionário com os dados do telefone, se for ID único.
                  Exemplo: {'id_telefone': 1, 'telefone': '11999999999'}
                - Uma lista de dicionários com os dados de todos os telefones encontrados, se for uma lista de IDs.

        Raises:
            mysql.connector.Error: Se ocorrer erro na consulta ao banco de dados.
        """
        try:
            self.db.cursor = self.db.connection.cursor(dictionary=True)

            # Se for uma lista de IDs
            if isinstance(ids_telefone, list):
                if not ids_telefone:
                    return []

                placeholders = ", ".join(["%s"] * len(ids_telefone))
                sql = f"SELECT * FROM telefones WHERE id_telefone IN ({placeholders})"
                self.db.cursor.execute(sql, ids_telefone)
                return self.db.cursor.fetchall()

            # Se for um ID único
            sql = "SELECT * FROM telefones WHERE id_telefone = %s"
            self.db.cursor.execute(sql, (ids_telefone,))
            telefone = self.db.cursor.fetchone()

            if telefone:
                print(f"✅ Telefone encontrado: {telefone}")
                return telefone
            else:
                print(f"⚠️ Telefone com ID {ids_telefone} não encontrado")
                return None

        except mysql.connector.Error as e:
            print(f"❌ Erro ao buscar telefone por ID: \n{e}")
            raise
        finally:
            if hasattr(self.db, "cursor") and self.db.cursor:
                self.db.cursor.close()

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
