import urllib.parse
import re
import time

import requests
from bs4 import BeautifulSoup as bs4


SEARCH_URL = 'https://db.netkeiba.com/'
ENCODING = 'EUC-JP'
WAIT_SECOND = 1


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
    検索結果のsoupからrace_idをすべて取り出す。
    """
    race_id_list = []
    tr_list = soup.find('table', class_='race_table_01').find_all('tr')
    for index, tr in enumerate(tr_list):
        # リストの先頭はヘッダーのため処理しない
        if index == 0: continue
        # classがtxt_lの要素は複数存在するがfindは最初に見つかった要素を返却するためこれでOK
        href = tr.find('td', class_='txt_l').a.get('href')
        race_id = get_id_from_href(href)
        race_id_list.append(race_id)
    return race_id_list


def make_race_info(race_id):
    """レース情報を抽出する

    Args:
        race_id (str): レースID

    Returns:
        dict[str, str]: レースの情報
    """
    url = f'{SEARCH_URL}race/{race_id}/'
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
        'race_id': race_id,
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


def make_race_horse_map_list(race_id):
    """レースの結果を抽出する

    Args:
        race_id (str): 

    Returns:
        list[dict[str, dict]]: 出走馬の情報リスト
    
    Note:
        プレミアム会員登録しないと閲覧できない場合は空のリストを返却する。
    """
    url = f'{SEARCH_URL}race/{race_id}/'
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
            'race_id'       : race_id,
            'horse_id'      : get_id_from_href(td_list[3].a.get('href')),
            'sex'           : td_list[4].string[0],
            'age'           : int(td_list[4].string[1]),
            'odds'          : float(td_list[12].string) if td_list[12].string != '---' else 'NULL',
            'umaban'        : int(td_list[2].string),
            'wakuban'       : int(td_list[1].string),
            'chakujun'      : int(td_list[0].string) if re.search('^[0-9]+$' ,td_list[0].string) else 'NULL',
            'jockey_id'     : get_id_from_href(td_list[6].a.get('href')),
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
    """馬の情報を抽出する

    Args:
        horse_id (str): 馬のID

    Returns:
        dict[str, str]: 馬の情報
    """
    url = f'{SEARCH_URL}horse/{horse_id}/'
    soup = get_soup_from_url(url, 'GET', None)

    horse_map = {
        'horse_id' : horse_id,
        'horse_name': soup.find('div', class_='horse_title').h1.string.strip()
    }

    # thのヘッダー名とDBのカラム、値変換処理の組み合わせ
    horse_column_map = {          
        '生年月日' :  {
            'key' : 'birthday',
            'val' : lambda td : to_date(td.string)
        },
        '調教師' : {
            'key' : 'trainer_id',
            'val' : lambda td : get_id_from_href(td.a.get('href'))
        },
        '馬主' : {
            'key' : 'owner_id',
            'val' : lambda td : get_id_from_href(td.a.get('href'))
        },
        '生産者' : {
            'key' : 'breeder_id',
            'val' : lambda td : get_id_from_href(td.a.get('href'))
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
    horse_map['father_horse_id'] = get_id_from_href(tr_list[0].find_all('td')[0].a.get('href'))
    horse_map['mother_horse_id'] = get_id_from_href(tr_list[2].find_all('td')[0].a.get('href'))

    # 過去の出走race_idをすべて取得
    past_race_id_list = []
    tr_list = soup.find('table', class_='db_h_race_results').find('tbody').find_all('tr')
    for tr in tr_list:
        past_race_id_list.append(get_id_from_href(tr.find_all('td')[4].a.get('href')))
    horse_map['past_race_id_list'] = past_race_id_list

    return horse_map


def trim(s):
    """文字列の前後の空白を削除する

    Args:
        s (str): 対象の文字列

    Returns:
        str: 前後の空白が削除された文字列
    """
    return str(s).strip()


def to_date(s):
    """日本語表記の日付をISOの拡張形式に変換する

    Args:
        s (str): 日付（YYYY年MM月DD日）

    Returns:
        str: 日付（YYYY-MM-DD）
    """
    return trim(s).replace('年','-').replace('月','-').replace('日','')


def get_id_from_href(href):
    """hrefからIDを取り出す

    Args:
        href (str): htmlのhref属性の値

    Returns:
        str: hrefに含まれるID

    Examples:
        >>> get_id_from_href('/horse/01234567/')
        '01234567'
    """
    # IDの規則性が不明であるため正規表現は使わない
    return (
        href.replace('/horse/ped/', '')
            .replace('/horse/', '')
            .replace('/race/', '')
            .replace('/breeder/', '')
            .replace('/trainer/', '')
            .replace('/owner/', '')
            .replace('/', '')
    )


def get_soup_from_url(url, method, payload):
    """urlへリクエストを送りレスポンスをsoupして返却する

    Args:
        url (str): URL
        method (str): GET or POST
        payload (:obj:dict[str, str], obtional): POST時に送信するpayload

    Returns:
        BeautifulSoup: レスポンスのHTMLのsoup
    
    TODO:
        * soupの型を調べる
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
