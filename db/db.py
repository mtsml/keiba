import os
import psycopg2


class Db:
    database_url = os.environ.get('KEIBA_DATABASE_URL')

    def get_connection(self):
        return psycopg2.connect(self.database_url)
