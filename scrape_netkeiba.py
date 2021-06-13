import urllib.parse
import re
import time

import requests
from bs4 import BeautifulSoup as bs4

from db.db import Db


SEARCH_URL = 'https://db.netkeiba.com/'
ENCODING = 'EUC-JP'
WAIT_SECOND = 1


def main(word, year):
    race_id_list = get_race_id_list(word, year)
    print('len: ', len(race_id_list))

    db = Db()
    for race_id in race_id_list:
        print('race_id: ', race_id)
        # 手作業で削除するためコメントアウト
        # db.delete_race(race_id)

        race_info = make_race_info(race_id)
        race_horse_map_info = make_race_horse_map_info(race_id)
        print('race_info: ', race_info)
        print('race_horse_map_info: ', race_horse_map_info)
        db.insert_race(race_info)
        if len(race_horse_map_info) > 0:
            db.insert_race_horse_map(race_horse_map_info)
            for i in race_horse_map_info:
                horse_id = i['horse_id']
                horse_info, past_race_id_list = make_horse_info(horse_id)
                print('  horse_info: ', horse_info)
                db.insert_horse(horse_info)

                # 過去の出走データ処理
                if len(past_race_id_list) > 0:
                    print('  past_race_id_list: ', past_race_id_list)
                    for past_race_id in past_race_id_list:
                        # race_idのデータはすでに追加済みのためスキップ
                        if race_id == past_race_id: continue
                        past_race_info = make_race_info(past_race_id)
                        past_race_horse_map_info = make_race_horse_map_info(past_race_id)
                        print('    past_race_info: ', past_race_info)
                        print('    past_race_horse_map_info: ', past_race_horse_map_info)
                        db.insert_race(past_race_info)
                        if len(past_race_horse_map_info) > 0:
                            db.insert_race_horse_map(past_race_horse_map_info)
                            # これ以上進む場合は再帰に置き換えること

        print('------------------------------------------')


def get_race_id_list(race_name, year):
    """
    race_nameにレース名が部分一致するすべてレースIDを取得する。
    """
    word = urllib.parse.quote(race_name, encoding=ENCODING)
    payload = {
        'pid': 'race_list',
        'list': '100',
        'start_year': year,
        'end_year': year,
        'word': word
    }

    soup = get_soup_from_url(SEARCH_URL, 'POST', payload)
    race_id_list = make_race_id_from_soup(soup)

    return race_id_list


def make_race_id_from_soup(soup):
    """
    soupからrace_idをすべて取り出す。
    """
    race_id_list = []
    tr_list = soup.find('table', class_='race_table_01').find_all('tr')
    for index, tr in enumerate(tr_list):
        # リストの先頭はヘッダーのため処理しない
        if index == 0: continue
        # classがtxt_lの要素は複数存在するがfindは最初に見つかった要素を返却するためこれでOK
        href = tr.find('td', class_='txt_l').a.get('href')
        race_id = href.replace('/race/', '').replace('/', '')
        race_id_list.append(race_id)
    return race_id_list


def make_race_info(race_id):
    """
    netkeibaからrace_idを元にhtmlを取得し、必要なレース情報を抽出して返却する。
    """
    url = f'https://db.netkeiba.com/race/{race_id}/'
    soup = get_soup_from_url(url, 'GET', None)

    race_name = soup.find('dl', class_='racedata').dd.h1.text.strip()
    serch_text = re.compile('.*天候.*')
    element = soup.find(text=serch_text)
    race_info = (element.string).split('\xa0/\xa0')[:3]
    mawari = (race_info[0])[1:2]
    distance = re.sub('[^0-9]+', '', race_info[0]) # 数字以外を削除
    weather = (race_info[1])[5:]
    track_type, track_condition = map(trim, race_info[2].split(':'))

    element = soup.find('p', attrs={ 'class': 'smalltxt' })
    race_basic_info = ((element.string).split())[0:3]
    race_date = to_date(race_basic_info[0])
    race_condition = race_basic_info[2]
    racecourse = re.findall('回(.*)\d+日', race_basic_info[1])[0]

    race_info = {
        'race_id': int(race_id),
        'race_name': race_name,
        'race_date': race_date,
        'weather': weather,
        'distance': int(distance),
        'racecourse': racecourse,
        'race_condition': race_condition,
        'track_type': track_type,
        'mawari': mawari,
        'track_condition': track_condition
    }
    return race_info


def make_race_horse_map_info(race_id):
    """
    netkeibaからrace_idを元にhtmlを取得し、必要な出走馬の情報を抽出して返却する。
    """
    url = f'https://db.netkeiba.com/race/{race_id}/'
    soup = get_soup_from_url(url, 'GET', None)

    race_horse_map_list = []
    if soup.find('div', class_='Premium_Regist_Box'):
        # プレミアム会員登録が必要な場合はデータを取得せずに返却する
        return race_horse_map_list

    tr_list = soup.find('table', class_='race_table_01').find_all('tr')
    for index, tr in enumerate(tr_list):
        # リストの先頭はヘッダーのため処理しない
        if index == 0: continue

        td_list = tr.find_all('td')
        race_horse_map = {
            'race_id'       : int(race_id),
            'horse_id'      : td_list[3].a.get('href').replace('/horse/', '').replace('/', ''),
            'sex'           : td_list[4].string[0],
            'age'           : int(td_list[4].string[1]),
            'odds'          : float(td_list[12].string) if td_list[12].string != '---' else 'NULL',
            'umaban'        : int(td_list[2].string),
            'wakuban'       : int(td_list[1].string),
            'chakujun'      : int(td_list[0].string) if re.search('^[0-9]+$' ,td_list[0].string) else 'NULL',
            'jockey_id'     : td_list[6].a.get('href').replace('/jockey/', '').replace('/', ''),
            'jockey_weight' : float(td_list[5].string) if td_list[5].string != None else 'NULL',
            'race_time'     : td_list[7].string if td_list[7].string != None else 'NULL',
            'weight'        : int(re.sub('\(.*\)', '', td_list[14].string)) if re.sub('\(.*\)', '', td_list[14].string) != '計不' else 'NULL',
            'agari'         : float(td_list[11].string) if td_list[11].string != None else 'NULL',
            'passing_order' : td_list[10].string,
            'prize'         : int(re.sub('\..*$', '', td_list[20].string).replace(',', ''))*10000 if td_list[20].string != None else 'NULL'
        }
        race_horse_map_list.append(race_horse_map)

    return race_horse_map_list


def make_horse_info(horse_id):
    url = f'https://db.netkeiba.com/horse/{horse_id}/'
    soup = get_soup_from_url(url, 'GET', None)

    horse_map = {
        'horse_id' : horse_id,
        'horse_name': soup.find('div', class_='horse_title').h1.string.strip()
    }

    horse_column_map = {          
        '生年月日' :  {
            'key' : 'birthday',
            'val' : lambda td : to_date(td.string)
        },
        '調教師' : {
            'key' : 'trainer_id',
            'val' : lambda td : td.a.get('href').replace('/trainer/', '').replace('/', '')
        },
        '馬主' : {
            'key' : 'owner_id',
            'val' : lambda td : td.a.get('href').replace('/owner/', '').replace('/', '')
        },
        '生産者' : {
            'key' : 'breeder_id',
            'val' : lambda td : td.a.get('href').replace('/breeder/', '').replace('/', '')
        },
        '産地' : {
            'key' : 'birthplace',
            'val' : lambda td : td.string
        },
        'セリ取引価格' : {
            'key' : 'selling_price',
            'val' : lambda td : int(re.sub('[^0-9]*', '', td.get_text('/').split('/')[0])) * 10000 if td.string != '\n-\n' else None
        }
    }

    # 馬のprofileを取得
    tr_list = soup.find('table', class_='db_prof_table').find_all('tr')
    for tr in tr_list:
        th = tr.find('th').string
        td = tr.find('td')
        if th in horse_column_map.keys():
            horse_map[horse_column_map[th]['key']] = horse_column_map[th]['val'](td)

    # 血統情報を取得　
    tr_list = soup.find('table', class_='blood_table').find_all('tr')
    horse_map['father_horse_id'] = tr_list[0].find_all('td')[0].a.get('href').replace('/horse/ped/', '').replace('/', '')
    horse_map['mother_horse_id'] = tr_list[2].find_all('td')[0].a.get('href').replace('/horse/ped/', '').replace('/', '')

    # 過去の出走race_idをすべて取得
    past_race_id_list = []
    tr_list = soup.find('table', class_='db_h_race_results').find('tbody').find_all('tr')
    for tr in tr_list:
        past_race_id_list.append(int(tr.find_all('td')[4].a.get('href').replace('/race/', '').replace('/', '')))

    return horse_map, past_race_id_list


def trim(s):
    """
    文字列の前後の空白を削除する。
    """
    return str(s).strip()


def to_date(s):
    """
    日本語表記の日付をISOの拡張形式に変換する。
    変換前：YYYY年MM月DD日
    返還後：YYYY-MM-DD
    """
    return trim(s).replace('年','-').replace('月','-').replace('日','')


def get_soup_from_url(url, method, payload):
    """
    urlへリクエストを送りレスポンスをparseして返却する。
    """
    # サーバー負荷軽減のため指定秒数待機する
    time.sleep(WAIT_SECOND)

    res = None
    if method == 'GET':
        res = requests.get(url)
    elif method == 'POST':
        res = requests.post(url, data=payload)
        res.encoding = ENCODING

    soup = bs4(res.content, 'lxml')
    return soup


if __name__ == "__main__":
    word = input('検索ワードを入力してください >')
    year = input('年度を入力してください      >')
    main(word, year)
