import urllib.parse
import re
import time

import requests
from bs4 import BeautifulSoup as bs4

# importするための対処療法（よくわからん）
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db import Db
from scrape.util import *


def main(word, year):
    # IO低減のためprintを絞っている
    race_id_list = get_race_id_list(word, year)
    print('len: ', len(race_id_list))

    db = Db()
    for race_id in race_id_list:
        print('race_id: ', race_id)
        race_info = make_race_info(race_id)
        race_horse_map_list = make_race_horse_map_list(race_id)
        db.insert_race(race_info)
        if len(race_horse_map_list) > 0:
            db.insert_race_horse_map(race_horse_map_list)
            for i in race_horse_map_list:
                horse_id = i['horse_id']
                horse_info = make_horse_info(horse_id)
                past_race_id_list = horse_info['past_race_id_list']
                print('  horse_id: ', horse_info['horse_id'])
                db.insert_horse(horse_info)

                # 過去の出走データ処理
                if len(past_race_id_list) > 0:
                    for past_race_id in past_race_id_list:
                        # race_idのデータはすでに追加済みのためスキップ
                        if race_id == past_race_id: continue
                        past_race_info = make_race_info(past_race_id)
                        past_race_horse_map_list = make_race_horse_map_list(past_race_id)
                        print('    past_race_id: ', past_race_info['race_id'])
                        db.insert_race(past_race_info)
                        if len(past_race_horse_map_list) > 0:
                            db.insert_race_horse_map(past_race_horse_map_list)
                            # これ以上進む場合は再帰に置き換えること

        print('------------------------------------------')


if __name__ == "__main__":
    word = input('検索ワードを入力してください >')
    year = input('年度を入力してください      >')
    main(word, year)
