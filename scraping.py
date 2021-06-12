from bs4 import BeautifulSoup as bs4
import re
import requests

target_url = 'https://db.netkeiba.com/race/202005030411/'

def make_race_list(url):
    res = requests.get(url)
    soup = bs4(res.content, 'lxml')
    # print(soup)

    serch_text = re.compile('.*天候.*')
    elements = soup.find_all(text=serch_text)
    for val in elements:
        race_info = (val.string).split('\xa0/\xa0')[:3]
        track_type = (race_info[0])[:1]
        mawari = (race_info[0])[1:2]
        distance = (race_info[0])[2:6]
        weather = (race_info[1])[5:]
        if (race_info[2])[:1] == '芝':
            track_condition = (race_info[2])[4:]
        elif (race_info[2])[:1] == 'ダ':
            track_condition = (race_info[2])[6:]
        else:
            track_condition = (race_info[2])[5:]

    elements = soup.find_all('p', attrs={ 'class': 'smalltxt' })
    for val in elements:
        race_basic_info = ((val.string).split())[1:3]
        race_condition = race_basic_info[1]
        racecource = ((re.findall('回(.*)日', race_basic_info[0]))[0])[:2]
    
    


    race_id = url[-13:-1]
    print(race_id)
    print(weather)
    print(distance)
    print(racecource)
    print(race_condition)
    print(track_type)
    print(mawari)
    print(track_condition)


# race_name = input('Enter Race name >> ')
make_race_list(target_url)


# race_id
# weather
# distance
# racecource
# race_conditon
# track_type
# track_condition