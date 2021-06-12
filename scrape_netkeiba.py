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
        race_info = make_race_list(race_id)
        print('race_info: ', race_info)
        db.insert_race(race_info)
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
    race_id_list = filter_race_id_from_soup(soup)

    return race_id_list


def filter_race_id_from_soup(soup):
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


def make_race_list(race_id):
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
    race_basic_info = ((element.string).split())[1:3]
    race_condition = race_basic_info[1]
    racecourse = re.findall('回(.*)\d+日', race_basic_info[0])[0]

    race_info = {
        'race_id': int(race_id),
        'weather': weather,
        'distance': int(distance),
        'racecourse': racecourse,
        'race_condition': race_condition,
        'track_type': track_type,
        'mawari': mawari,
        'track_condition': track_condition
    }
    return race_info


def trim(s):
    """
    文字列の前後の空白を削除する。
    """
    return str(s).strip()


if __name__ == "__main__":
    word = input('検索ワードを入力してください>')
    main(word)