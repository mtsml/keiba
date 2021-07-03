import traceback

# importするための対処療法（よくわからん）
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.db import Db
from scrape.util import *


SEARCH_URL = 'https://race.netkeiba.com/'
ENCODING = 'EUC-JP'
WAIT_SECOND = 1


def sub(race_id):
    """レース情報を抽出する

    Args:
        race_id (str): レースID

    Returns:
        dict[str, str]: レースの情報
    """
    url = f'{SEARCH_URL}race/shutuba.html?race_id={race_id}'
    soup = get_soup_from_url(url, 'GET', None)

    race_horse_map_list = []
    tr_list = soup.find('table', class_='RaceTable01').find_all('tr')
    for index, tr in enumerate(tr_list):
        # リストの先頭はヘッダーのため処理しない
        if index in (0,1): continue
        td_list = tr.find_all('td')
        race_horse_map = {
            'race_id'       : race_id,
            'horse_id'      : get_id_from_href(td_list[3].div.div.find('span', class_='HorseName').a.get('href').replace('https://db.netkeiba.com', '')),
            'sex'           : td_list[4].string[0],
            'age'           : int(td_list[4].string[1]),
            'odds'          : 'NULL', #float(td_list[9].span.string.replace(',', '')),
            'umaban'        : int(td_list[1].string),
            'wakuban'       : int(td_list[0].span.string),
            'jockey_id'     : get_id_from_href(td_list[6].a.get('href')),
            'jockey_weight' : float(td_list[5].string),
            'weight'        : 'NULL', #int(re.sub('\(.*\)', '', td_list[14].string)) if re.sub('\(.*\)', '', td_list[14].string) != '計不' else 'NULL',
            'chakujun'      : 'NULL',
            'race_time'     : 'NULL', #to_time(td_list[7].string) if not isNull(td_list[7].string) else 'NULL',
            'agari'         : 'NULL', #float(td_list[11].string) if not isNull(td_list[11].string) else 'NULL',
            'passing_order' : 'NULL', #td_list[10].string if td_list[10].string != None else 'NULL',
            'prize'         : 'NULL' #int(re.sub('\..*$', '', td_list[20].string).replace(',', ''))*10000 if td_list[20].string != None else 'NULL'
 
        }
        race_horse_map_list.append(race_horse_map)

    return race_horse_map_list


def main(race_id):
    error_horse_id_list = []    
    db = Db()
    print('race_id: ', race_id)
    race_horse_map_list = sub(race_id)
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
                    # 過去の出走データが全て登録済みの場合はスキップ
                    if db.count_race_horse_map(horse_id) == len(past_race_id_list):
                        print('  過去レース登録済みのためスキップ')
                        continue
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
                print(traceback.format_exc())
                error_horse_id_list.append(horse_id)
                pass
    print('おわったよ。')
    print('Error horse_id_list: ', error_horse_id_list)

"""
当日のレースデータを取得する
"""
if __name__ == "__main__":
    race_id = input('レースIDを入力してください >')
    main(race_id)
