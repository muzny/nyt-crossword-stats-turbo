import requests
import json
import datetime
from datetime import date
import pandas as pd
# from tqdm import tqdm
import argparse


# A = argparse.ArgumentParser(
#     description='Gets data from NYT crosswords for puzzles',
#     formatter_class=argparse.ArgumentDefaultsHelpFormatter
# )
# A.add_argument('-o', '-out_file', action='store', type=str,
#     help="The output path where data should be saved (e.g. out.csv)")


# https://github.com/kesyog/crossword
# Each puzzle is assigned a numerical id. Before we can fetch the stats for a given puzzle, 
# we need to know that id. To find it, send a GET request as below, specifying {start_date} and {end_date} in 
# YYYY-MM-DD format (ISO 8601). 
# The server response is limited to 100 puzzles and can be limited further by adding a limit parameter.
# have to ask for 100 days at a time

# params: ?publish_type=daily&date_start=2023-01-01&date_end=2024-01-13

PUZZLE_IDS_ENDPOINT = "https://www.nytimes.com/svc/crosswords/v3/36569100/puzzles.json"

# To fetch solve stats for a given puzzle, send a GET request as below, replacing {id} with the puzzle id. This API requires a NYT crossword subscription. {subscription_header} can be found by snooping on outgoing HTTP requests via Chrome/Firefox developer tools while opening a NYT crossword in your browser. Alternatively, you can supposedly extract your session cookie from your browser and send that instead (see linked reddit post below), but I haven't tried it myself.
GAME_SOLVE_ENDPOINT = "https://www.nytimes.com/svc/crosswords/v6/game/"

# curl 'https://www.nytimes.com/svc/crosswords/ v3/36569100/puzzles.json?publish_type=daily&date_start={start_date}&date_end={end_date}' -H 'accept: application/json'

def get_day_incs(start_date, end_date, inc = 100) -> list:

    begin = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_day = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    delta = end_day - begin
    dates = [begin]
    
    while delta.days > 100:
        next_day = dates[-1] + datetime.timedelta(days=inc)
        dates.append(next_day)
        delta = end_day - dates[-1]

    # add the last day
    dates.append(end_day)

    return dates

def get_puzzle_info(start_date: str, end_date: str, cookie: str = None, publish_type: str = "daily") -> list:
    headers = {'content-type': 'application/json'}
    # this endpoint will  work with no 'Cookie', but it won't get you as much information
    payload = {'date_start': start_date, 'date_end': end_date, 'publish_type': publish_type}
    r = requests.get(PUZZLE_IDS_ENDPOINT, headers = headers, params = payload)
    # print(r.url)
    results = r.json()['results']

    return results

    

def get_solve_info(results: list, cookie: str) -> list:
    headers = {'content-type': 'application/json',
               'Cookie': cookie}
    # this endpoint will not work with no cookie

    # endpoint ends with {id}.json
    timed_puzzles = []
    for id_res in results:
        # skip ones that you've filled nothing in for
        if id_res['percent_filled'] == 0:
            continue
    
        id = id_res['puzzle_id']
        r = requests.get(GAME_SOLVE_ENDPOINT + str(id) + ".json", headers = headers)
        calcs = r.json()['calcs']
        if len(calcs) > 0:
            # {'percentFilled': 100, 'secondsSpentSolving': 886, 'solved': True}
            copy_res = id_res.copy()
            copy_res.update(calcs)
            timed_puzzles.append(copy_res)
    
    return timed_puzzles

def get_complete_info(start_date: str, end_date: str, cookie: str, verbose = True) -> pd.DataFrame:
    date_incs = get_day_incs(start_date, end_date)
    all_results = []
    for i in range(len(date_incs) - 1):
        start = datetime.datetime.strftime(date_incs[i], "%Y-%m-%d")
        # exclusive end for no repeats
        end = datetime.datetime.strftime(date_incs[i + 1] - datetime.timedelta(days=1), "%Y-%m-%d")
        print(start, "->", end)
        results = get_puzzle_info(start, end, cookie)
        results_time = get_solve_info(results)
        all_results += results_time

    print(len(all_results))
    return pd.DataFrame(all_results)

cookie = 
df = get_complete_info("2023-01-01", "2024-01-14", cookie)
print(df.head())
# write it to a csv
df.to_csv("data.csv")
# results = get_puzzle_info("2023-01-01", "2023-03-01")
# results_time = get_solve_info(results)
