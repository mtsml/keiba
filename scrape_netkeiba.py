import urllib.parse
import re

import requests
from bs4 import BeautifulSoup as bs4

from db.db import Db


SEARCH_URL = 'https://db.netkeiba.com/'
ENCODING = 'EUC-JP'


def main(word):
    race_id_list = get_race_id_list(word)
    print('len: ', len(race_id_list))

    db = Db()
    for race_id in race_id_list:
        print('race_id: ', race_id)
        race_info = make_race_info(race_id)
        race_horse_map_info = make_race_horse_map_info(race_id)
        print('race_info: ', race_info)
        print('race_horse_map_info: ', race_horse_map_info)
        db.insert_race(race_info)
        if len(race_horse_map_info) > 0:
            db.insert_race_horse_map(race_horse_map_info)
        return
        print('------------------------------------------')


def get_race_id_list(race_name):
    """
    race_nameにレース名が部分一致するすべてレースIDを取得する。
    """
    word = urllib.parse.quote(race_name, encoding=ENCODING)
    payload = {
        'pid': 'race_list',
        'list': '100',
        'word': word
    }
    res = requests.post(SEARCH_URL, data=payload)

    res.encoding = ENCODING
    soup = bs4(res.text, 'lxml')
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
    res = requests.get(url)
    soup = bs4(res.content, 'lxml')

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
    res = requests.get(url)
    soup = bs4(res.content, 'lxml')

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
            'horse_id'      : int(td_list[3].a.get('href').replace('/horse/', '').replace('/', '')),
            'odds'          : float(td_list[12].string) if td_list[12].string != '---' else 'NULL',
            'umaban'        : int(td_list[2].string),
            'wakuban'       : int(td_list[1].string),
            'chakujun'      : int(td_list[0].string) if re.search('^[0-9]+$' ,td_list[0].string) else 'NULL',
            'jockey_id'     : int(td_list[6].a.get('href').replace('/jockey/', '').replace('/', '')),
            'race_time'     : td_list[7].string if td_list[7].string != None else 'NULL',
            'weight'        : int(re.sub('\(.*\)', '', td_list[14].string)) if re.sub('\(.*\)', '', td_list[14].string) != '計不' else 'NULL',
            'agari'         : float(td_list[11].string) if td_list[11].string != None else 'NULL',
            'passing_order' : td_list[10].string
        }
        race_horse_map_list.append(race_horse_map)
    
    return race_horse_map_list


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


if __name__ == "__main__":
    word = input('検索ワードを入力してください>')
    main(word)