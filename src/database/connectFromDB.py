import mysql.connector
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
        self.cursor = self.connection.cursor(dictionary=True)
        self.verificarConexao()

    # METODOS:
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

    def searchIDFromDataBase(self, idClient: int, coluna: str, tabela: str):
        """Busca o ID  no banco baseado no cpf

        Args:
            idClient (int): CPF do cliente.
            tabela (str): tabela a ser procurado
            coluna (str) : coluna a ser procurado

        Returns:
            int | None: ID do encontrado, senão None.

        Raises:
            mysql.connector.Error: Se ocorrer erro na consulta.
        """
        try:
            sql = "SELECT %s FROM %s WHERE cpf = %s"
            self.cursor.execute(sql, (coluna, tabela, idClient))
            resultado = self.cursor.fetchone()
            return resultado[0] if resultado else None
        except mysql.connector.Error as e:
            print(f"❌ Erro ao buscar telefone do cliente: \n {e}")
            return None

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


# exemplo de uso
if __name__ == "__main__":
    db = Database()
    db.verificarConexao()
    db.fecharConexao()
