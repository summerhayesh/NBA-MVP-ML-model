import pandas as pd, Utils, os

def clean():
    """
    Creates a dataframe containing MVP, per-game and team data, then saves to a .csv
    """
    if not Utils.data_exists("../csvFiles/mvp-pg-team (clean).csv"):
        # Initialises necessary dataframes from .csv files
        MVP_df, Pg_df, team_df = df_initializer()

        # Merges the per-game and MVP dataframes, and matches rows
        # based on the "Player" and "year" columns in an outer join
        pg_mvp_df = Pg_df.merge(MVP_df, how="outer", on=["Player", "year"])

        # Maps the return of nkname_dict() to values in the "Team" column
        pg_mvp_df["Team"] = pg_mvp_df["Team"].map(nkname_dict())
        complete_df = pg_mvp_df.merge(team_df, how="outer", on=["Team", "year"]).fillna(0)
        complete_df = col_d_type(complete_df)
        complete_df = diagnostics(complete_df)
        complete_df.to_csv("../csvFiles/mvp-pg-team (clean).csv", index=False)
        print("\nFinished cleaning")
    else:
        print("\nmvp-pg-team.csv already exists - this will be used for training")


def col_d_type(df):
    """
    Reassigns incorrect column data types
    :param df: Dataframe,
        The dataframe being modified
    :return: dataframe,
        The corrected dataframe
    """
    # Replaces "—" with "0" in the "GB" column
    df["GB"] = df["GB"].str.replace("—", "0")

    # Making the "GB" column a numeric column, rather than an object column
    df["GB"] = pd.to_numeric(df["GB"])
    return df


def diagnostics(df):
    """
    Adds diagnostic columns to our dataframe, for to help train the ML model
    :param df: Dataframe,
        the dataframe being modifying
    :return:
        The modified dataframe
    """
    df = add_ratios(df)
    df = pos_tm_cat(df)
    df = MVP_label(df)
    return df

def pos_tm_cat(df):
    """
    Adds a column which assigns a numerical value for position (str) and team (str)
    :param df: Dataframe,
        the dataframe being modified
    :return:
        the modified dataframe
    """

    # Converts the "Pos" and "Team" columns into a "categorical" d-type, then gets the
    # numerical codes associated with each unique value/category in that column
    df["NPos"] = df["Pos"].astype("category").cat.codes
    df["NTm"] = df["Team"].astype("category").cat.codes
    return df

def add_ratios(df):
    """
    Adds the ratio of, the value in the specified column to the mean of its column (for that year),
    to the dataframe.
    :param df: dataframe,
        The dataframe having the ratio column added to it
    :return: dataframe,
        the modified dataframe
    """
    # Groups the columns by year, then divides each value in each column by the mean of that column
    ratios = df[["PTS", "AST", "STL", "BLK", "3P", "year"]].groupby("year").apply(lambda x: x / x.mean())
    ratios = ratios.reset_index(drop=True)

    # Adds the ratio columns for each row to the main dataframe
    df[["PTS_R", "AST_R", "STL_R", "BLK_R", "3P_R"]] = ratios[["PTS", "AST", "STL", "BLK", "3P"]]
    return df

def MVP_label(df):
    """
    Adds an MVP column, defining whether a player won MVP (1 = MVP, 0 = Non-MVP)
    :param df: dataframe,
        the dataframe having the MVP column added to it
    :return: dataframe,
        the modified dataframe
    """

    # Getting only those who won MVP in a given year
    MVPs = df.sort_values('Share', ascending=False).groupby('year').first().reset_index()

    # Creating an MVP column, defining whether a player won MVP (1 = MVP, 0 = Non-MVP)
    df['MVP'] = df.apply(lambda x: 1 if x['Player'] in MVPs['Player'].unique().tolist() \
                and x['Age'] in MVPs.loc[(MVPs.Player == x['Player'])]['Age'].unique().tolist() else 0, axis=1)
    return df

def df_initializer():
    """
    :return: dataframe,
        Initialises dataframes for MVP, per-game and team data
    """

    # Initialising MVP dataframe - but only need these columns
    MVPs = pd.read_csv("../csvFiles/MVPs.csv")[["Player", "year", "First", "Pts Won", "Pts Max", "Share", "WS", "WS/48"]]

    # Reads the Per-game data file, then cleans it
    if not Utils.data_exists("../csvFiles/Per-game (clean).csv"):
        print("\nCleaning Per-game data...")
        Per_game = pg_clean(pd.read_csv("../csvFiles/Per-game.csv"))
        os.remove("../csvFiles/Per-game.csv")
    else:
        print("\nPer-game data already clean")
        Per_game = pd.read_csv("../csvFiles/Per-game (clean).csv")

    # Normalises all the team names
    if not Utils.data_exists("../csvFiles/Team-stats (clean).csv"):
        print("\nCleaning team data...")
        Teams = tm_clean(pd.read_csv("../csvFiles/Team-stats.csv"))
        os.remove("../csvFiles/Team-stats.csv")
    else:
        print("\nTeam data already clean")
        Teams = pd.read_csv("../csvFiles/Team-stats (clean).csv")

    return MVPs, Per_game, Teams

def nkname_dict():
    """
    :return: dict,
        Creates a dictionary mapping team abbreviations (str) to the teams full name (str)
    """
    nicknames = {}
    with open("../csvFiles/nicknames.csv") as f:

        # Outputs the file as:
        # ['Abbreviation,Name\n', 'ATL,Atlanta Hawks\n', 'BRK,Brooklyn Nets\n', ...]
        lines = f.readlines()
        for line in lines[1:]:

            # Creating a tuple of team abbreviation, with team name
            abbrev, team = line.replace("\n", "").split(",")
            nicknames[abbrev] = team
    return nicknames


def tm_clean(df):
    """
    Reformats team names in the "team" column (series) using regex
    :param df: dataframe,
        team dataframe we're cleaning.
    :return: clean dataframe
    """
    # replaces ("*") values in team names, e.g. "Orlando Magic*", with ""
    df["Team"] = (df["Team"].str.replace(r"\*", "", regex=True)
                  # replaces suffixes indicating team seed that season ("*\xao(int)"), e.g. "Orlando Magic*\xa0(7)"
                  .str.replace(r"\u00A0\(\d{1,2}\)", "",  regex=True))
    df.to_csv("../csvFiles/Team-stats (clean).csv")
    return df

def pg_clean(df):

    # Cleans pg df by applying row_combiner() to each row, then resets the index
    Per_game = df.groupby(["Player", "year"]).apply(row_combiner).reset_index(drop=True)
    del Per_game["Rk"]
    Per_game.to_csv("../csvFiles/Per-game (clean).csv", index=False)
    return Per_game


def row_combiner(df):
    """
    Combines rows (dataframe), where a player has multiple rows for a single year, into one row
    :param df: dataframe,
        dataframe containing per-game/mvp data
    :return: dataframe,
        a single row for a players season, either unchanged or combined depending on if they played for multiple teams
    """
    if df.shape[0] == 1: # If number of rows of the current dataframe is just 1
        return df
    else:

        # Gets the row from the current dataframe which has the players averages for that season
        row = df[df['Team'] == '2TM']

        # Sets the value of the "Team" column, to the last "Team" the player played for that year
        row["Team"] = df.iloc[-1]["Team"]
        return row