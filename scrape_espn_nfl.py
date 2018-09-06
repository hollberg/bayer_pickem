import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import lxml
import requests

test_game_id = '401030690'

def get_game_ids():
    """
    17 weeks in season
    :return:
    """
    WEEKLY_SCHEDULE_URL_PREFIX = r'http://www.espn.com/nfl/schedule/_/week/'

    for week in range(1,18):    # 17 Weeks in a season

        schedule_page = requests.get(WEEKLY_SCHEDULE_URL_PREFIX + str(week))
        schedule_soup = BeautifulSoup(schedule_page.content, 'lxml')

        # Looking for <a> links like:
        # <a data-dateformat="time1" name="xxx" href="/nfl/game?gameId=401030690">8:20 PM</a>
        for a in schedule_soup.findAll('a',attrs={'data-dateformat':'time1'}):
            game_id = a['href'].replace('/nfl/game?gameId=', '')
            game_time = str(a.parent['data-date'])
            #print(f'{game_id}, {str(week)}')
            yield(game_id, str(week), game_time)


def parse_gamepage(game_id):
    """
    Given the ESPN Game ID, navigate to game page and scrape win probability
    and other relvant data
    :param game_id:
    :return:
    """
    gamepage_url_prefix = r'http://www.espn.com/nfl/game?gameId='
    gamepage = requests.get(gamepage_url_prefix+game_id)
    gamepage_soup = BeautifulSoup(gamepage.content, 'lxml')



    return gamepage_soup


# for game_id, week, time in get_game_ids():
#     print(f'{game_id}, {week}, {time}')

game = parse_gamepage(test_game_id)

game_title = game.find_all('title')


moo = 'boo'

