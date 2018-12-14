import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import csv
import lxml
import openpyxl
import requests
import datetime

import scratch

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
    save_html_locally(dir_path='game_scrapes/wk15/',
                      game_id=game_id,
                      html = gamepage.text)
    # timestamp = datetime.datetime.today().date()
    # fname = f'game_scrapes/wks_all/{game_id}_{str(timestamp)}.html'
    # with open(f'{fname}', 'w') as fh:
    #     fh.write(gamepage.text)
    #     fh.close()

    gamepage_soup = BeautifulSoup(gamepage.content, 'lxml')
    return gamepage_soup


def get_game_results(week_begin: int, week_end: int):
    col_heading = ['game_id, game_week, team_name, team_result, team_score']
    for week in range(week_begin, week_end):
        for game in scratch.get_game_results(week):

            result_dict = dict()
            result_dict['team1'] = (game['game_id'],game['game_week'],game['team1']['name'],
                  game['team1']['result'],game['team1']['score'])
            result_dict['team2'] = (game['game_id'],game['game_week'],game['team2']['name'],
                  game['team2']['result'],game['team2']['score'])

            yield result_dict

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

    df_raw_games = tuples_to_df(get_games(wk_begin=week_begin), col_names=col_names)

    # Make copy, dropping the "Away" team columns
    df_home = df_raw_games.drop(labels=['away_team', 'away_win_pct'], axis=1)
    df_home['IsHome'] = 1
    df_home.rename(index=str, columns={'home_team': 'team', 'home_win_pct': 'win_pct'}, inplace=True)

    # Make copy, dropping the "Home" team columns
    df_away = df_raw_games.drop(labels=['home_team', 'home_win_pct'], axis=1)
    df_away['IsHome'] = 0
    df_away.rename(index=str, columns={'away_team': 'team', 'away_win_pct': 'win_pct'}, inplace=True)

    # Append "Home" and "Away" dataframes
    df_forecasts = df_home.append(df_away)
    df_forecasts.set_index('game_id', inplace=True)

    df_forecasts.to_excel(filename)


def stack_submissions():
    """kasdkdk
    """
    submission_xl = r'picks_wk15.xlsx'
    df = pd.read_excel(submission_xl)
    df.set_index('Person', inplace=True)

    # Replace blanks with NaNs
    df.replace(to_replace = '', value=np.nan, inplace=True)
    # Replace 'X' values with week 17 (will never count)
    df.replace(to_replace = 'X', value=17, inplace=True)
    # df.index = df.index.set_names(['Person', 'Team'])
    df_out = df.stack(dropna=True).to_frame()
    df_out.index = df_out.index.set_names(['Person', 'Team'])
    df_out.columns = ['Week']

    xl_writer = pd.ExcelWriter('stacked_picks.xlsx')
    df_out.to_excel(xl_writer, merge_cells=False)
    xl_writer.save()


# build_game_ids_file('game_ids_2018.csv')
# **Run "print_games(wk_num) below to update**
## make_forecast_file(17, 'myfile.xlsx')



stack_submissions()

# for entry in get_game_ids(1):
#     print(entry)

# results_list = []
# for entry in get_game_results(13,14):
#     moo = 'boo'
#     results_list.append(entry['team1'])
#     results_list.append(entry['team2'])
#
# df_test = pd.DataFrame(results_list)
# df_test.to_excel('results.xlsx')
#
#
# # print(get_game_results(12,13))
#
# make_forecast_file(15, 'forecasts.xlsx')