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
            self.garantir_conexao()
            print(f"❌ Erro ao se conectar ao Banco de dados: \n {e}")

    def abrirConexao(self):
        """Abre (ou reabre) a conexão com o banco de dados MySQL e o cursor.

        Este método é seguro para ser chamado após uma desconexão ou falha na conexão.
        Ele atualiza `self.connection` e `self.cursor` com uma nova sessão.

        Raises:
            mysql.connector.Error: Se ocorrer erro na conexão com o banco.
        """
        try:
            print("🌐 Estabelecendo nova conexão com o banco de dados...")
            self.connection = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_DATABASE"),
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print("✅ Nova conexão estabelecida com sucesso.")
        except mysql.connector.Error as e:
            print(f"❌ Falha ao abrir a conexão com o banco: {e}")
            raise

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

    def garantir_conexao(self):
        """garante a conexão"""
        if not self.connection.is_connected():
            print("🔄 Reconectando ao banco de dados...")
            self.connection.reconnect(attempts=3, delay=2)
        if not hasattr(self, "cursor") or self.cursor is None:
            self.cursor = self.connection.cursor()

    def searchIDFromDataBase(self, cpf: str, coluna: str, tabela: str):
        """Busca o ID  no banco baseado no cpf

        Args:
            idClient (cpf): CPF do cliente.
            tabela (str): tabela a ser procurado
            coluna (str) : coluna a ser procurado

        Returns:
            int | None: ID do encontrado, senão None.

        Raises:
            mysql.connector.Error: Se ocorrer erro na consulta.
        """
        try:
            self.abrirConexao()
            sql = f"SELECT {coluna} FROM {tabela} WHERE cpf = %s"
            self.cursor.execute(sql, (cpf,))
            resultado = self.cursor.fetchone()
            return resultado[coluna] if resultado else None
        except mysql.connector.Error as e:
            print(f"❌ Erro ao buscar telefone do cliente: \n {e}")
            return None
        finally:
            self.fecharConexao()

    def atualizarRegistro(
        self, tabela: str, valores_dict: dict, campo_where: str, valor_where
    ):
        """
        Atualiza registros de forma genérica em qualquer tabela.

        Args:
            tabela (str): Nome da tabela a ser atualizada.
            valores_dict (dict): Dicionário com campos e novos valores.
            campo_where (str): Campo da cláusula WHERE.
            valor_where (Any): Valor do campo da cláusula WHERE.

        Returns:
            bool: True se a atualização for bem-sucedida, False caso contrário.

        Raises:
            mysql.connector.Error: Se ocorrer erro ao executar a atualização.
        """
        if not valores_dict:
            print("⚠️ Nenhum campo foi fornecido para atualização.")
            return False

        try:
            self.abrirConexao()

            campos_sql = [f"`{campo}` = %s" for campo in valores_dict.keys()]
            valores = list(valores_dict.values())
            valores.append(valor_where)

            # Usar backticks para evitar conflitos com palavras reservadas e SQL injection em nomes de colunas/tabelas
            sql = f"UPDATE `{tabela}` SET {', '.join(campos_sql)} WHERE `{campo_where}` = %s"

            self.cursor.execute(sql, tuple(valores))
            self.connection.commit()
            print(f"✅ Registro atualizado com sucesso na tabela '{tabela}'!")
            return True

        except mysql.connector.Error as e:
            print(f"❌ Erro ao atualizar registro na tabela '{tabela}':\n{e}")
            return False

        finally:
            self.fecharConexao()


# exemplo de uso
if __name__ == "__main__":
    db = Database()
    db.verificarConexao()
    db.fecharConexao()
