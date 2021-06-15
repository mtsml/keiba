import traceback

# importするための対処療法（よくわからん）
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db import Db
from scrape.util import *


def main(horse_id):
    """馬の情報と過去の出走レース情報を登録する

    Args:
        horse_id (str): 馬のID
        doSkip (str): 過去レースが登録済みの場合に処理を終了するか
    """
    error_race_id_list = []
    db = Db()
    try:
        horse_info = make_horse_info(horse_id)
        print('horse_name: ', horse_info['horse_name'])
        past_race_id_list = horse_info['past_race_id_list']
        db.insert_horse(horse_info)

        # 過去の出走データ処理
        if len(past_race_id_list) > 0:
            if db.count_race_horse_map(horse_id) == len(past_race_id_list):
                print('過去レース登録済みのため終了')
                return
            for past_race_id in past_race_id_list:
                print('  past_race_id: ', past_race_id)
                past_race_info = make_race_info(past_race_id)
                past_race_horse_map_list = make_race_horse_map_list(past_race_id)
                print('  past_race_name: ', past_race_info['race_name'])
                db.insert_race(past_race_info)
                if len(past_race_horse_map_list) > 0:
                    db.insert_race_horse_map(past_race_horse_map_list)
    except:
        print(traceback.format_exc())
        error_race_id_list.append(past_race_id)
        pass
    finally:
        print('------------------------------------------')
    print('おわったよ。')
    print('Error race_id_list: ', error_race_id_list)


if __name__ == "__main__":
    horse_id = input('馬のIDを入力してください >')
    main(horse_id)
