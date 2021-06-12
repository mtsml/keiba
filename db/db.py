import os
import psycopg2


class Db:
    database_url = os.environ.get('KEIBA_DATABASE_URL')

    def get_connection(self):
        return psycopg2.connect(self.database_url)

    def insert_race(self, race_info):
        """
        レース情報をraceテーブルに格納する。
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO race(race_id, weather, distance, racecourse, race_condition, track_type, track_condition, mawari) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)',
                   (race_info['race_id'], race_info['weather'], race_info['distance'], race_info['racecourse'], race_info['race_condition'], race_info['track_type'], race_info['track_condition'], race_info['mawari']))
            conn.commit()