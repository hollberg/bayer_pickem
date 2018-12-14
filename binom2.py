""" Model Results of multiple events, where each event has a separate probability"""


import random
from collections import defaultdict
import pandas as pd

# william = [.715, .553, .885, .784, .866, .633]
# doug = [.715, .735, .626, .316, .568, .597]

league_dict = {'william': [.890, .771, .862, .706],
               'casey': [.550, .771, .594, .750],
               'doug': [0, .318, .594, .583],
               'christine': [.340, .316, .862, .248],
               'tammy': [.700, .318, .594, .292]}

initial_dict = {0:0, 1:0, 2:0, 3:0, 4:0}
best_other_res = {0:0, 1:0, 2:0, 3:0, 4:0}

league_res_dict = defaultdict(dict)

h2h_dict = {'Win': 0, 'Loss':0, 'Tie': 0}


def run_trial(event_probs):
    """
    given a list of event probabilities, return
    number of successes for a single trial
    :param event_probs: List containing float probabilites
    :return: Integer number of successful results
    """
    successes = 0
    for event in event_probs:
        if event >= random.random():
            successes += 1

    return successes


def trial_results(num_trials, event_probs):
    """
    Run trials 'num_trials' times, return dict with binned results
    :param num_trials: Number of trials to run
    :param event_probs: List containing even probabilities
    :return:
    """
    results_dict = {0:0, 1:0, 2:0, 3:0, 4:0}
    for trial in range(num_trials):
        output = run_trial(event_probs)
        results_dict[output] = results_dict[output] + 1

    return results_dict


for person, odds in league_dict.items():
    league_res_dict[person] = trial_results(10000,odds)

    print(f'{person}: {league_res_dict[person]}')


# Head to Head
for _ in range(10000):

    william_wins, other_wins, best_other = 0, 0, 0
    for person, odds in league_dict.items():
        if person == 'william':
            william_wins = run_trial(odds)
        else:
            other_wins = run_trial(odds)
            best_other = max(other_wins, best_other)

    best_other_res[best_other] = best_other_res[best_other] + 1
    if william_wins > best_other:
        h2h_dict['Win'] = h2h_dict['Win'] + 1
    elif william_wins == best_other:
        h2h_dict['Tie'] = h2h_dict['Tie'] + 1
    else:
        h2h_dict['Loss'] = h2h_dict['Loss'] + 1

print(f'Best Other: {best_other_res}')
print(h2h_dict)

# print(league_res_dict)

# will_results = trial_results(1000, william)
# doug_results = trial_results(1000, doug)

moo = 'boo'