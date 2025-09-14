import datetime, pandas as pd, os
from pathlib2 import Path

def unique_yrs():
    df = pd.read_csv("../csvFiles/mvp-pg-team (clean).csv")
    years = df["year"].unique().tolist()
    first_year = min(years)
    last_yr = max(years)
    return first_year, last_yr

def yr_classifier(yr, current_yr):
    if yr == "P":
        return current_yr
    elif isinstance(yr, (bool, int)):
        return yr
    else:
        for char in yr:
            if not char.isdigit() or not yr:
                return False
        else:
            return int(yr)

def year_input(caller):
    current_yr = datetime.datetime.now().year
    if caller == "training":

        first_yr, last_yr = unique_yrs()

        print("\nWhen training the model, the end year for must be at least 5 years greater than the start year, "
              "so the model has some data to be trained on")
    else:
        first_yr, last_yr = 1955, current_yr
    print(f"\nThe available years for {caller} are from {first_yr} to {last_yr}")
    start_yr = (input("\nStart year: "))
    end_yr = input("\nEnd year (input 'P' to toggle the current year): ")
    start_yr, end_yr = input_checker(start_yr, end_yr, first_yr, last_yr, current_yr, caller)
    return start_yr, end_yr
    
def input_checker(start_yr, end_yr, first_yr, last_yr, current_yr, caller):
    start_yr = yr_classifier(start_yr, current_yr)
    end_yr = yr_classifier(end_yr, current_yr)

    # When user picks an invalid start or end year
    while not start_yr or not end_yr:
        if not start_yr:
            start_yr = input("\nStart year picked is not a valid input"
                         f" Pick a year greater than or equal to {first_yr} and less than or equal to {last_yr}")
            input_checker(start_yr, end_yr, first_yr, last_yr, current_yr, caller)
        else:
            end_yr = input("\nEnd year picked is not a valid input"
                             f" Pick a year greater than the picked start year ({start_yr}) and less than or equal to {last_yr}")
            input_checker(start_yr, end_yr, first_yr, last_yr, current_yr, caller)

    # When the user picks a start year that is not within the specified range
    while not first_yr <= start_yr <= last_yr:
        print(f"\nStart year picked ({start_yr}) is not within the the specified range of years available")
        start_yr = (input(f"Pick a year greater than or equal to {first_yr} and less than or equal to {last_yr}: "))
        input_checker(start_yr, end_yr, first_yr, last_yr, current_yr, caller)
        
    # When the user picks an end year that is not within the specified range
    while not first_yr <= end_yr <= last_yr:
        print(f"\nEnd year picked ({end_yr}) is not within the specified range of years available")
        end_yr = input(f"Pick a year greater than the picked start year ({start_yr}) and less than or equal to {last_yr} "
                       f"(input 'P' to toggle the current year): ")
        input_checker(start_yr, end_yr, first_yr, last_yr, current_yr, caller)
        
    # When the start year is greater than the end year or vice versa
    while start_yr > end_yr:
        print(f"\nStart year must be less than the end year")
        start_yr = input(f"pick a year greater than {first_yr} and less than {last_yr}")
        input_checker(start_yr, end_yr, first_yr, last_yr, current_yr, caller)
        
    if caller == "training":

        # When the user doesn't give at least 5 years' worth of training data to train the model on
        while start_yr + 5 > end_yr:
            print(f"\nEnd year picked ({end_yr}) is not at least 5 years after the selected start year ({start_yr})\n"
                  f"The model needs at least 5 years worth of training data before it can make predictions ")
            end_yr = input(f"\nPick an end year that is at least 5 years in the future from {start_yr}, "
                           f"e.g. from {start_yr + 5} onwards (input 'P' to toggle the current year): ")
            input_checker(start_yr, end_yr, first_yr, last_yr, current_yr, caller)    
    return start_yr, end_yr

    
def data_exists(file_path):
    """
    Checks if a file for a specified year (int) exists, and whether it's empty
    :param file_path, str:
        path of file
    :return: boolean,
        boolean indicating if we already possess the data for this year
    """
    file = Path(file_path)
    if file.exists():
        file_size = os.path.getsize(file)
        if file_size == 0:
            return False # File exists, but there's nothing inside it
        else:
            return True  # File exists, but it's not empty
    else:
        return False