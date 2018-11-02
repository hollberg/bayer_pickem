import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import csv
import lxml
import requests
import datetime

test_game_id = '401030775'

def get_game_ids(wk_begin: int = 1):
    """
    wk_begin: Integer, week of season from which to scrape
    17 weeks in season
    :return:
    """
    WEEKLY_SCHEDULE_URL_PREFIX = r'http://www.espn.com/nfl/schedule/_/week/'

    for week in range(wk_begin,18):    # 17 Weeks in a season

        schedule_page = requests.get(WEEKLY_SCHEDULE_URL_PREFIX + str(week))
        schedule_soup = BeautifulSoup(schedule_page.content, 'lxml')

        # Looking for <a> links like:
        # <a data-dateformat="time1" name="xxx" href="/nfl/game?gameId=401030690">8:20 PM</a>
        for a in schedule_soup.findAll('a',attrs={'data-dateformat':'time1'}):
            game_id = a['href'].replace('/nfl/game?gameId=', '')
            game_id = game_id.replace('/nfl/game/_/gameId/', '')    # Alternate URL prefix to clean
            game_time = str(a.parent['data-date'])
            #print(f'{game_id}, {str(week)}')
            yield(game_id, str(week), game_time)


def build_game_ids_file(output_file):
    col_headers = ['GameID', 'Week', 'Time']

    with open(output_file, mode='w') as game_ids_file:
        game_ids_writer = csv.writer(
            game_ids_file, delimiter=',',
            quotechar='"', quoting=csv.QUOTE_MINIMAL)

        game_ids_writer.writerow(col_headers)

        for game_id, game_week, game_time in get_game_ids():
            game_ids_writer.writerow([game_id, game_week, game_time])


def save_html_locally(dir_path:str, game_id:str, html):
    """Save the HTML of the current page"""
    timestamp = datetime.datetime.today().date()
    fname = f'{dir_path}/{game_id}_{str(timestamp)}.html'
    with open(f'{fname}', 'w') as fh:
        fh.write(html)
        fh.close()

    return True


def parse_gamepage(game_id):
    """
    Given the ESPN Game ID, navigate to game page and scrape win probability
    and other relvant data
    :param game_id:
    :return: Beautiful Soup object of
    """
    gamepage_url_prefix = r'http://www.espn.com/nfl/game?gameId='
    gamepage = requests.get(gamepage_url_prefix + game_id)

    # Save HTML Content of game locally
    save_html_locally(dir_path='game_scrapes/wk9/',
                      game_id=game_id,
                      html = gamepage.text)
    # timestamp = datetime.datetime.today().date()
    # fname = f'game_scrapes/wks_all/{game_id}_{str(timestamp)}.html'
    # with open(f'{fname}', 'w') as fh:
    #     fh.write(gamepage.text)
    #     fh.close()

    gamepage_soup = BeautifulSoup(gamepage.content, 'lxml')
    return gamepage_soup


def print_games(wk_begin: int = 1):
    """
    :param wk_begin: Integer; first week of data to collect
    :return:
    """
    print('Title, GameID, Week#, Time, Home, Home Win %, Away, Away Win %')
    for game_id, week, time in get_game_ids(wk_begin):
        game = parse_gamepage(game_id)

        game_title = game.find_all('title')[0].text

        home_team = game.find('span', {'class': 'home-team'}).text
        away_team = game.find('span', {'class': 'away-team'}).text

        # NOTE: Home/Away win Percentages MISLABELED in ESPN's HTML;
        # Thus assign home_win_pct to the "value-away" class and vice versa!
        home_win_pct = game.find('span', {'class': 'value-away'}).text
        away_win_pct = game.find('span', {'class': 'value-home'}).text

        print(f'{game_title},{game_id},{week},{time},{home_team},\
              {home_win_pct},{away_team},{away_win_pct}')


# build_game_ids_file('game_ids_2018.csv')
# **Run "print_games(wk_num) below to update**
print_games(8)

# for entry in get_game_ids(1):
#     print(entry)


moo = 'bools'

