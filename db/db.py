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

    def insert_race_horse_map(self, race_horse_map_list):
        sql = 'INSERT INTO public.race_horse_map(race_id, horse_id, odds, umaban, wakuban, chakujun, jockey_id, race_time, weight, agari, passing_order) VALUES '
        for index, race_horse_map in enumerate(race_horse_map_list):
            if index != 0:
                sql += ','
            race_time_tmp = "'" if race_horse_map['race_time'] != 'NULL' else ''
            sql += f"({race_horse_map['race_id']}, {race_horse_map['horse_id']}, {race_horse_map['odds']}, {race_horse_map['umaban']}, {race_horse_map['wakuban']}, {race_horse_map['chakujun']}, {race_horse_map['jockey_id']}, {race_time_tmp}{race_horse_map['race_time']}{race_time_tmp}, {race_horse_map['weight']}, {race_horse_map['agari']}, '{race_horse_map['passing_order']}')"

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()