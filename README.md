Running
---
```
python get_stats.py [--outfile outfile.csv] [--kind [summaries|full]] --start YYYY-MM-DD --end YYYY-MM-DD --cookie 'your cookie here in single quotes'
```

Default value for `--outfile` is `data.csv`, default value for `--kind` is `summaries`. `start` is inclusive, `end` is exclusive.

To get your cookie value (this will be a long string), here is one strategy: 
1. Log in to NYT Crosswords via a website
2. Open the page inspector (on Firefox, "Inspect")
3. Click the "Network" tab
4. Find a GET request to `www.nytimes.com` that looks like `crosswords?login=email&auth=login-email`, click this
5. Under "Request Headers", look for the field `Cookie`
6. Copy+paste your entire cookie (as an example, mine is 2527 characters long)

Endpoints & Data
---
From the general puzzle id & info endpoint (`https://www.nytimes.com/svc/crosswords/v3/36569100/puzzles.json?date_start={start date}&date_end={end date}&publish_type=daily`, where start and end dates are in format `yyyy-mm-dd`), we get results in the format:

```
{"status":"OK","results":[{"author":"Gia Bosko","editor":"Will Shortz","format_type":"Normal","print_date":"2023-04-10","publish_type":"Daily","puzzle_id":20953,"title":"","version":0,"percent_filled":0,"solved":false,"star":null},{"author":"John Ewbank","editor":"Will Shortz","format_type":"Normal","print_date":"2023-04-09","publish_type":"Daily","puzzle_id":20961,"title":"If the Clue Fits ...","version":0,"percent_filled":100,"solved":true,"star":"Gold"}]}
```
Note that this endpoint is accessible without providing your cookie. In this case, you'll get less info (the last puzzle does not indicate solved in this case):

```
{"status":"OK","results":[{"author":"Gia Bosko","editor":"Will Shortz","format_type":"Normal","print_date":"2023-04-10","publish_type":"Daily","puzzle_id":20953,"title":"","version":0,"percent_filled":0,"solved":false,"star":null},{"author":"John Ewbank","editor":"Will Shortz","format_type":"Normal","print_date":"2023-04-09","publish_type":"Daily","puzzle_id":20961,"title":"If the Clue Fits ...","version":0,"percent_filled":0,"solved":false,"star":null}]}
```

From the solve info endpoint, which requires the correct cookie (`https://www.nytimes.com/svc/crosswords/v6/game/20961.json`):

```
{"board":{"cells":[{"guess":"F","timestamp":1},...]},
"calcs":{"percentFilled":100,"secondsSpentSolving":1834,"solved":true},"firsts":{"cleared":1681057721,"opened":1681057643,"solved":1681059477},"lastCommitID":"xxxxx","puzzleID":20961,"timestamp":1681059478,"userID":XXXXXX,"minGuessTime":1681057686,"lastSolve":1681059477}
```
If you do not pass your cookie you will get an ERROR.

The fields under "firsts" do not use milliseconds since epoch (`https://currentmillis.com/`), but I'm currently unsure what unit they do use.

"board" format
------
Cell 0 (the cell at index 0 in the "cells" list) is in the upper left.
Cell 1 is to the right of cell 0.
Cells that are blocked/black are marked as "blank": true.
Cells that have a guess have the fields "guess": "letter" and "timestamp" : number of seconds elapsed since puzzle start when it was entered.

On a Sunday crossword (21 x 21), cell 21 is the first cell in the second row, cell 42 is the first cell in the third row, etc. Cell 440 is the last cell in the lower right.

On a daily crossword (15 x 15), cell 15 is the first cell in the second row, cell 30 is the first cell in the third row, etc. Cell 224 is the last cell in the lower right.

Every so often (e.g., "2023-09-19") there is a puzzle that is neither 21 x 21 nor 15 x 15 (e.g., 14 x 16 has 224 cells instead of 225). This makes us annoyed.


Other resources/notes
---
Some other resources say that you only need the `NYT-S` part of the cookie, but I haven't been able to get that to work yet.

https://github.com/kesyog/crossword has a rust library for getting data from the NYT crossword enpoints.

https://github.com/michadenheijer/pynytimes has a great general NYT API library in python.


