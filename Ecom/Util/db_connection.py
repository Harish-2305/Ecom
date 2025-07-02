import mysql.connector

class DBconnection:
    __connection=None

    @staticmethod

    def get_connection():
        if DBconnection.__connection is None:
            db_config = {
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': '230524',
                'database': 'Ecom'
            }
            DBconnection.__connection=mysql.connector.connect(**db_config)
        return DBconnection.__connection
