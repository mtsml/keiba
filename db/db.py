import os
import psycopg2


class Db:
    """
    DB操作を行うクラス。
    """

    database_url = os.environ.get('KEIBA_DATABASE_URL')

    def get_connection(self):
        """
        database_urlのDBへの接続を確立する。
        """
        return psycopg2.connect(self.database_url)

    def backup(self, table_name):
        """
        対象のテーブルのバックアップを取得する。
        """
        # TODO: 実装する

    def delete_race(self, race_id):
        """
        race_idに関連するテーブルをすべて空にする。
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('DELETE FROM race_horse_map WHERE race_id = %s; DELETE FROM race WHERE race_id = %s; DELETE FROM horse WHERE EXISTS (SELECT 1 FROM race_horse_map WHERE horse_id = horse.horse_id AND race_id = %s);', (race_id, race_id, race_id))
            conn.commit()

    def insert_race(self, race_info):
        """
        レース情報をraceテーブルに格納する。
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO race(race_id, race_name, race_date, weather, distance, racecourse, race_condition, track_type, track_condition, mawari) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  ON CONFLICT (race_id) DO NOTHING',
                   (race_info['race_id'], race_info['race_name'], race_info['race_date'], race_info['weather'], race_info['distance'], race_info['racecourse'], race_info['race_condition'], race_info['track_type'], race_info['track_condition'], race_info['mawari']))
            conn.commit()

    def insert_race_horse_map(self, race_horse_map_list):
        """
        出走馬の情報をrace_horse_mapテーブルに一括で格納する。
        形式：INSERT INTO race_horse_map VALUES(),(),();
        """
        sql = 'INSERT INTO public.race_horse_map(race_id, horse_id, age, sex, odds, umaban, wakuban, chakujun, jockey_id, jockey_weight, race_time, weight, agari, passing_order, prize) VALUES '
        for index, race_horse_map in enumerate(race_horse_map_list):
            if index != 0:
                sql += ','
            # race_timeは文字列のためNULLでない場合は「'」を付与する
            race_time_tmp = "'" if race_horse_map['race_time'] != 'NULL' else ''
            sql += f"('{race_horse_map['race_id']}', '{race_horse_map['horse_id']}', {race_horse_map['age']}, '{race_horse_map['sex']}', {race_horse_map['odds']}, {race_horse_map['umaban']}, {race_horse_map['wakuban']}, {race_horse_map['chakujun']}, '{race_horse_map['jockey_id']}', {race_horse_map['jockey_weight']}, {race_time_tmp}{race_horse_map['race_time']}{race_time_tmp}, {race_horse_map['weight']}, {race_horse_map['agari']}, '{race_horse_map['passing_order']}', {race_horse_map['prize']})"
        sql += '  ON CONFLICT (race_id, horse_id) DO NOTHING'
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
    
    def insert_horse(self, horse_info):
        """
        レース情報をhorseテーブルに格納する。
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO horse(horse_id, horse_name, birthday, trainer_id, owner_id, breeder_id, birthplace, selling_price, father_horse_id, mother_horse_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (horse_id) DO NOTHING",
                   (horse_info['horse_id'], horse_info['horse_name'], horse_info['birthday'], horse_info['trainer_id'], horse_info['owner_id'], horse_info['breeder_id'], horse_info['birthplace'], horse_info['selling_price'], horse_info['father_horse_id'], horse_info['mother_horse_id']))
            conn.commit()