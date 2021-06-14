import urllib.parse
import re
import time
import traceback

import requests
from bs4 import BeautifulSoup as bs4

# importするための対処療法（よくわからん）
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db import Db
from scrape.util import *


def main(word, year):
    error_race_id_list = []
    error_horse_id_list = []
    
    race_id_list = get_race_id_list(word, year)
    print('len: ', len(race_id_list))

    db = Db()
    for race_id in race_id_list:
        try:
            print('race_id: ', race_id)
            race_info = make_race_info(race_id)
            print('race_name: ', race_info['race_name'])
            race_horse_map_list = make_race_horse_map_list(race_id)
            db.insert_race(race_info)
            if len(race_horse_map_list) > 0:
                db.insert_race_horse_map(race_horse_map_list)
                for i in race_horse_map_list:
                    horse_id = i['horse_id']
                    print('  horse_id: ', horse_id)
                    try:
                        horse_info = make_horse_info(horse_id)
                        print('  horse_name: ', horse_info['horse_name'])
                        past_race_id_list = horse_info['past_race_id_list']
                        db.insert_horse(horse_info)

                        # 過去の出走データ処理
                        if len(past_race_id_list) > 0:
                            for past_race_id in past_race_id_list:
                                # race_idのデータはすでに追加済みのためスキップ
                                if race_id == past_race_id: continue
                                print('    past_race_id: ', past_race_id)
                                past_race_info = make_race_info(past_race_id)
                                past_race_horse_map_list = make_race_horse_map_list(past_race_id)
                                print('    past_race_name: ', past_race_info['race_name'])
                                db.insert_race(past_race_info)
                                if len(past_race_horse_map_list) > 0:
                                    db.insert_race_horse_map(past_race_horse_map_list)
                                    # これ以上進む場合は再帰に置き換えること
                    except:
                        traceback.format_exc()
                        error_horse_id_list.append(horse_id)
                        pass
        except:
            traceback.format_exc()
            error_race_id_list.append(race_id)
            pass
        finally:
            print('------------------------------------------')
    print('おわったよ。')
    print('Error race_id_list: ', error_race_id_list)
    print('Error horse_id_list: ', error_horse_id_list)


if __name__ == "__main__":
    word = input('検索ワードを入力してください >')
    year = input('年度を入力してください      >')
    main(word, year)
