import requests
import json
import datetime
import pandas as pd
# from tqdm import tqdm
import argparse


A = argparse.ArgumentParser(
    description='Gets data from NYT crosswords for puzzles',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
A.add_argument('-c', '--cookie', action='store', type=str,
    help="Your full cookie from NYT (e.g. nyt-a=...), enclosed in single quotes")
A.add_argument('-o', '--outfile', action='store', type=str, default="data.csv",
    help="The output path where data should be saved (e.g. data.csv)")
A.add_argument('-v', '--verbose', action='store_true')
A.add_argument('-k', '--kind', action='store', type=str, default="summaries",
               help="The kind of data to get ('summaries' or 'full')")
A.add_argument('-s', '--start', action='store', type=str, 
               help="Date to start gathering data from (inclusive) in format YYYY-MM-DD")
A.add_argument('-e', '--end', action='store', type=str, 
               help="Date to stop gathering data from (exclusive) in format YYYY-MM-DD")


# https://github.com/kesyog/crossword
# Each puzzle is assigned a numerical id. Before we can fetch the stats for a given puzzle, 
# we need to know that id. To find it, send a GET request as below, specifying {start_date} and {end_date} in 
# YYYY-MM-DD format (ISO 8601). 
# The server response is limited to 100 puzzles and can be limited further by adding a limit parameter.
# have to ask for 100 days at a time

# params: ?publish_type=daily&date_start=2023-01-01&date_end=2024-01-13
PUZZLE_IDS_ENDPOINT = "https://www.nytimes.com/svc/crosswords/v3/36569100/puzzles.json"

# To fetch solve stats for a given puzzle, send a GET request as below, replacing {id} with the puzzle id. 
# This API requires a NYT crossword subscription. {subscription_header} can be found by snooping on outgoing 
# HTTP requests via Chrome/Firefox developer tools while opening a NYT crossword in your browser. 
# Alternatively, you can supposedly extract your session cookie from your browser and send that instead 
# (see linked reddit post below), but I haven't tried it myself.
GAME_SOLVE_ENDPOINT = "https://www.nytimes.com/svc/crosswords/v6/game/"



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

def get_puzzle_ids(start_date: str, end_date: str, cookie: str = None, publish_type: str = "daily") -> list:
    # this endpoint will  work with no 'Cookie', but it won't get you as much information
    headers = {'content-type': 'application/json',
               'Cookie': cookie}
    
    payload = {'date_start': start_date, 'date_end': end_date, 'publish_type': publish_type}

    r = requests.get(PUZZLE_IDS_ENDPOINT, headers = headers, params = payload)
    print(r.url)
    results = r.json()['results']

    return results

    

def get_solve_info(results: list, cookie: str, summaries: bool = True) -> list:
    headers = {'content-type': 'application/json',
               'Cookie': cookie}
    # this endpoint will not work with no cookie

    # endpoint ends with {id}.json
    timed_puzzles = []
    if results is None:
        return timed_puzzles
    for id_res in results:
        # skip ones that you've filled nothing in for
        if id_res['percent_filled'] == 0:
            continue
    
        id = id_res['puzzle_id']
        r = requests.get(GAME_SOLVE_ENDPOINT + str(id) + ".json", headers = headers)
        
        print(r.url)
        print(id_res["print_date"])
        board = r.json()['board']['cells']
        calcs = r.json()['calcs']
        if len(calcs) > 0:
            # {'percentFilled': 100, 'secondsSpentSolving': 886, 'solved': True}
            copy_res = id_res.copy()
            copy_res.update(calcs)
            if not summaries:
                blank_cells = [ind for ind in range(len(board)) if "blank" in board[ind]]
                guess_cells = [board[ind]["guess"] if "guess" in board[ind] else False for ind in range(len(board))]
                time_cells = [board[ind]["timestamp"] if "timestamp" in board[ind] else False for ind in range(len(board))]
                # blank_cells = {'cell' + str(ind) + "_blank": True if "blank" in board[ind] else False for ind in range(len(board))}
                # guess_cells = {'cell' + str(ind) + "_guess": board[ind]["guess"] if "guess" in board[ind] else False for ind in range(len(board))}
                # time_cells = {'cell' + str(ind) + "_timestamp": board[ind]["timestamp"] if "timestamp" in board[ind] else False for ind in range(len(board))}
                # cells = {ind: cells[ind] for ind in range(len(cells))}
                print(len(blank_cells), len(guess_cells), len(time_cells))
                copy_res["blanks"] = blank_cells
                copy_res["guesses"] = guess_cells
                copy_res["times"] = time_cells
                # copy_res.update(time_cells)
                # copy_res['cells'] = board
            timed_puzzles.append(copy_res)
    
    return timed_puzzles

def get_complete_info(start_date: str, end_date: str, cookie: str, summaries: bool = True, verbose = True) -> pd.DataFrame:
    date_incs = get_day_incs(start_date, end_date)
    all_results = []
    for i in range(len(date_incs) - 1):
        start = datetime.datetime.strftime(date_incs[i], "%Y-%m-%d")
        # exclusive end for no repeats
        end = datetime.datetime.strftime(date_incs[i + 1] - datetime.timedelta(days=1), "%Y-%m-%d")
        print(start, "->", end)
        results = get_puzzle_ids(start, end, cookie)
        results_time = get_solve_info(results, cookie, summaries)
        all_results += results_time

    print("Number of puzzles with data recorded: ", len(all_results))
    return pd.DataFrame(all_results)

if __name__ == "__main__":
    args = A.parse_args()
    cookie = args.cookie
    print("Cookie length: ", len(cookie))
    df = get_complete_info(args.start, args.end, cookie, args.kind == "summaries")
    print(df.head())
    # write it to the specified file
    df.to_csv(args.outfile, index = False)
