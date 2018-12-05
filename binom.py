""" Model Results of multiple events, where each event has a separate probability"""


import random
from collections import defaultdict
import pandas as pd

william = [.715, .553, .885, .784, .866, .633]
doug = [.715, .735, .626, .316, .568, .597]


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
    results_dict = defaultdict(int)
    for trial in range(num_trials):
        output = run_trial(event_probs)
        results_dict[output] = results_dict[output] + 1

    return results_dict

will_results = trial_results(1000, william)
doug_results = trial_results(1000, doug)

moo = 'boo'
print(will_results)

# df_will = pd.DataFrame(will_results)
# df_doug = pd.DataFrame(doug_results)

# Head to head
wins = 0
ties = 0
for _ in range(1000):
    will_wins = run_trial(william)
    doug_wins = run_trial(doug)
    if will_wins > doug_wins:
        wins = wins + 1
    elif will_wins == doug_wins:
        ties += 1

print(f'William Wins: {str(wins)}')
print(f'Ties: {str(ties)}')