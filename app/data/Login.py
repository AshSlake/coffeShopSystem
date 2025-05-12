from ConnectFromDB import Database


class Login:
    def __init__(self, db: Database):
        self.db = db

    def add_login(self, cpf, password):
        sql = "INSERT INTO Login (cpf, senha) VALUES (%s, %s)"
        params = (cpf, password)
        self.db.cursor.execute(sql, params)

    def validate_login(self, cpf, password):
        sql = "SELECT * FROM Login WHERE cpf = %s AND senha = %s"
        params = (cpf, password)
        result = self.db.cursor.fetch_one(sql, params)
        return result is not None
