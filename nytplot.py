import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import argparse
import json
import ast # for literal_eval
A = argparse.ArgumentParser(
    description='Makes plots from NYT crossword data',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
A.add_argument('-i', '--infile', action='store', type=str, default="data.csv",
    help="The input path where data should be read from (e.g. data.csv)")



def weekday_counts_plot(df):
    # print date has the date in it
    print(df["day_of_week"].value_counts())
    sns.countplot(x="day_of_week", data=df)
    plt.show()

def weekday_trends_plot(df, day):
    sns.scatterplot(x="print_date", y="secondsSpentSolving", data=df,
                 hue="day_of_week")
    plt.show()

def puzzle_solve_plot(puzzle_row):
    # get the puzzle structure with guesses and timestamps
    # (and blank cells)
    # and plot it

    guesses = ast.literal_eval(puzzle_row["guesses"])
    blanks = ast.literal_eval(puzzle_row["blanks"])
    times = ast.literal_eval(puzzle_row["times"])
    solve_time = puzzle_row["secondsSpentSolving"]

    # start at the top of the plot, so we need to figure out how
    # many rows there are
    if len(guesses) != 225 and len(guesses) != 441:

        print("Puzzle should have 225 or 441 cells, but has", len(guesses), "instead.")
        return None
    
    cells_per_row = 15 if len(guesses) == 225 else 21
    rows = cells_per_row

    xs = []
    ys = []
    colors = []
    alphas = []

    # make the plot into a square
    plt.figure(figsize=(10, 10))


    for row_num in range(rows):
        for col_num in range(cells_per_row):            
            xs.append(rows - row_num)
            ys.append(col_num)
            if (row_num * cells_per_row) + col_num in blanks:
                colors.append("black")
                alphas.append(1)
            else:
                # now, shade this cell based on how long it took to solve
                cell_time = times[(row_num * cells_per_row) + col_num]

                ratio = cell_time / solve_time
                if ratio > 1:
                    print("Cell time is greater than solve time!")
                    print("Cell time:", cell_time)
                    print("Solve time:", solve_time)
                alphas.append(ratio)
                colors.append("purple")
    # markers should be squares that fill the space
    size = 525 if cells_per_row == 21 else 900
    plt.scatter(xs, ys, c=colors, marker="s", s=size, alpha=alphas)
    plt.show()

def display_date_menu(df):
    # print the dates in the dataframe along with their day
    # names and their solve times
    for i in range(len(df)):
        row = df.iloc[i]
        print(i, ":", row["print_date"], row["day_of_week"], row["secondsSpentSolving"])
    # then get a puzzle to display from the user
    puzzle_num = input("Enter a puzzle number to display: ")
    puzzle_row = df.iloc[int(puzzle_num)]
    return puzzle_row

    

if __name__ == "__main__":
    args = A.parse_args()
    df = pd.read_csv(args.infile)
    # add in day of week name
    # because we'll probably want it for a lot of these plots
    print(df.head())
    df["day_of_week"] = df["print_date"].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").strftime("%A"))
    print(df.shape)
    print(df.dtypes)
    # weekday_counts_plot(df)
    # weekday_trends_plot(df, "Monday")
    # print(df.iloc[0])
    puzzle_row = display_date_menu(df)
    puzzle_solve_plot(puzzle_row)