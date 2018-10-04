import requests
from bs4 import BeautifulSoup
import lxml


def get_results(wk_num: int = 1):
    """
    Scrape game results for completed weeks
    :param wk_num: The week of the season for which to pull results
    :return:
    """
    RESULTS_URL_PREFIX = 'http://www.espn.com/nfl/schedule/_/week/'

    result_page = requests.get(RESULTS_URL_PREFIX + str(wk_num))
    result_soup = BeautifulSoup(result_page.content, 'lxml')

    # Looking for <a> links like:
    # <a name="&lpos=nfl:schedule:score" href="/nfl/game?gameId=401030710">PHI 18, ATL 12</a>
    for a in result_soup.findAll('a', {'name' : '&lpos=nfl:schedule:score'}):
        # <a> text of format "CIN 34, IND 23"
        res_text = a.text.replace(',','')   # Remove Comma
        game_id = a.attrs['href'].replace('/nfl/game?gameId=','')
        team1, team1_score, team2, team2_score = res_text.split()[0:4]
        team1_score = int(team1_score)
        team2_score = int(team2_score)

        # Check for Ties!
        if team1_score > team2_score:
            team1_result = 'W'
            team2_result = 'L'
        elif team1_score == team2_score:    # If Tie
            team1_result = 'T'
            team2_result = 'T'
        else:
            team1_result = 'L'
            team2_result = 'W'

        result = dict()
        result['game_id'] = game_id
        result['game_week'] = str(wk_num)
        result['team1'] = {'name': team1,
                           'result': team1_result,
                           'score': team1_score}
        result['team2'] = {'name': team2,
                           'result': team2_result,
                           'score': team2_score}

        yield result


def print_results():
    print(f'game_id, game_week, team_name, team_result, team_score')
    for week in range(1,5):
        for game in get_results(week):
            # print(game)
            print(f"{game['game_id']},{game['game_week']},{game['team1']['name']},"
                  f"{game['team1']['result']},{game['team1']['score']}")
            print(f"{game['game_id']},{game['game_week']},{game['team2']['name']},"
                  f"{game['team2']['result']},{game['team2']['score']}")



def get_powerrank():
    """
    Get team standings per https://thepowerrank.com/nfl/
    :return:
    """
    rank_page = requests.get('https://thepowerrank.com/nfl/')
    rank_soup = BeautifulSoup(rank_page.content, 'lxml')

    chart = rank_soup('div', {'id': 'chart'})
    moo = 'boo'
    return moo


get_powerrank()
