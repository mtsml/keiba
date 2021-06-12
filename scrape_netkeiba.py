import urllib.parse

import requests
from bs4 import BeautifulSoup


SEARCH_URL = 'https://db.netkeiba.com/'
ENCODING = 'EUC-JP'


def main(word):
    race_id_list = get_race_id_list(word)
    print(race_id_list)
    print(len(race_id_list))
    return
    for race_id in race_id_list:
        race_info = get_race_info(race_id)
        insert_race_info(race_info)


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
    soup = BeautifulSoup(res.text, 'html.parser');
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


def insert_race_info(race_info):
    """
    DBにレース情報を格納する。
    """

if __name__ == "__main__":
    word = input('検索ワードを入力してください>')
    main(word)