"""
scrape2.py
Scrape Game Forecast Data, output to Excel and/or *.csv
"""

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import csv
import os
import lxml
import openpyxl
import requests
import datetime


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


def save_html_locally(dir_path:str, game_id:str, html):
    """Save the HTML of the current page"""
    timestamp = datetime.datetime.today().date()
    fname = os.path.abspath(f'{dir_path}/{game_id}_{str(timestamp)}.html')
    with open(fname, 'w') as fh:
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
    save_html_locally(dir_path='game_scrapes/wk12',
                      game_id=game_id,
                      html = gamepage.text)
    # timestamp = datetime.datetime.today().date()
    # fname = f'game_scrapes/wks_all/{game_id}_{str(timestamp)}.html'
    # with open(f'{fname}', 'w') as fh:
    #     fh.write(gamepage.text)
    #     fh.close()

    gamepage_soup = BeautifulSoup(gamepage.content, 'lxml')
    return gamepage_soup


def get_games(wk_begin: int = 1):
    """
    :param wk_begin: Integer; first week of data to collect
    :return:
    """
    # print('Title, GameID, Week#, Time, Home, Home Win %, Away, Away Win %')
    for game_id, week, time in get_game_ids(wk_begin):
        game = parse_gamepage(game_id)

        game_title = game.find_all('title')[0].text

        home_team = game.find('span', {'class': 'home-team'}).text
        away_team = game.find('span', {'class': 'away-team'}).text

        # NOTE: Home/Away win Percentages MISLABELED in ESPN's HTML;
        # Thus assign home_win_pct to the "value-away" class and vice versa!
        home_win_pct = game.find('span', {'class': 'value-away'}).text
        away_win_pct = game.find('span', {'class': 'value-home'}).text

        yield(game_title, game_id , week, time, home_team,
              home_win_pct, away_team, away_win_pct)


def tuples_to_df(tuple_generator, col_names):
    """
    Given an iterable returning tuples, write to a file.
    See: https://stackoverflow.com/questions/42999332
    :param tuple_generator: Iterable YIELDING tuples of data
    :param col_names: Column Names/Heading (List)
    :return: Pandas DataFrame
    """
    data_list = [entry for entry in tuple_generator]
    df = pd.DataFrame(data_list, columns=col_names)

    return df


def make_forecast_file(week_begin: int, filename: str):
    """
    Create an Excel file with weekly forecasts
    :param week_begin: Integer, beginning week
    :param filename: String, output file path+name
    :return:
    """
    col_names = ['Game Title', 'game_id', 'week', 'time', 'home_team',
                 'home_win_pct', 'away_team', 'away_win_pct']

    df_raw_games = tuples_to_df(get_games(wk_begin=week_begin),col_names=col_names)
    print(df_raw_games.head())

    # Make copy, dropping the "Away" team columns
    df_home = df_raw_games.drop(labels=['away_team', 'away_win_pct'], axis = 1)
    df_home['IsHome'] = 1
    df_home.rename(index=str, columns={'home_team': 'team', 'home_win_pct': 'win_pct'}, inplace=True)

    # Make copy, dropping the "Home" team columns
    df_away = df_raw_games.drop(labels=['home_team', 'home_win_pct'], axis = 1)
    df_away['IsHome'] = 0
    df_away.rename(index=str, columns={'away_team': 'team', 'away_win_pct': 'win_pct'}, inplace=True)

    # Append "Home" and "Away" dataframes
    df_forecasts = df_home.append(df_away)

    df_forecasts.to_excel(filename)

moo = 'boo'

make_forecast_file(11,'forecast11.xlsx')