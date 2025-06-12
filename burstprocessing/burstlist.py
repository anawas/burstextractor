"""
Reads a burst list compiled by C. Monstein from server and processes its data
version 1.3
author: Andreas Wassmer
project: Raumschiff
"""
import datetime
import os
import re
import pandas as pd
import requests

import utils.timeutils

BASE_URL = "http://soleil.i4ds.ch/solarradio/data/BurstLists/2010-yyyy_Monstein"

def find_start_of_data(filename: str) -> int:
    """
    The format of the burst list has changed around mit 2024. Before then
    there where 8 lines of comment. After that, the file has 11 lines. 
    In order to maintain backwards compatibility we try to estimate the 
    file version read in.

    Args:
        filename (str): The path to the burstlist

    Returns:
        int: Number of header rows
    """
    date_regex = re.compile(r'^\d{8}\b')
    
    with open(filename, "r", encoding="utf-8") as f:
        for index, line in enumerate(f, start=0):
            if date_regex.match(line):
                return index
    return 0

def process_burst_list(filename, date=None) -> pd.DataFrame:
    """
    Let's discard the entries with missing data.
    These events have a time stamp of "##:##-##:##" with no further data
    in the row except the date. I like to use a conditional for filtering.
    I think the filter is more readable. Especially if there are several
    conditions. If the user wants the data of a specific day this data
    is extracted as well.

    Returns: A Pandas Dataframe with valid events
    """
    
    data_start = find_start_of_data(filename)
    col_names = ['Date', 'Time', 'Type', 'Instruments']
    data = pd.read_csv(filename, sep="\t+", skiprows=data_start, skipfooter=4,
                       index_col=False, encoding="latin-1",
                       names=col_names, engine="python")

    # on some random occasions the date is in int format. Set this to string
    data['Date'] = data['Date'].astype('string')
    missing_conditional = data['Time'] != "##:##-##:##"
    cleaned = data.loc[missing_conditional]

    if date is not None:
        date_conditional = cleaned['Date'] == date
        cleaned = cleaned.loc[date_conditional]

    return cleaned


def download_burst_list(select_year, select_month):
    """
    The burst list contains all (manually) detected radio bursts per
    month and year. This function gets the file from the server, if
    necessary (i.e. not available or older than 6 hrs.)
    Parameters:
    int:year of the event
    int:month of the event

    Returns:
    str:the filename of the list.
    I decided not to return the content but rather the
    location of the file. This keeps the data for further
    processing with other tools if needed.
    """

    # Check for valid date has been done in main
    year, month, day = utils.timeutils.adjust_year_month_day(
        select_year, select_month
    )
    filename = f"e-CALLISTO_{year}_{month}.txt"
    if burstlist_exists(filename):
        return filename
    flare_list = requests.get(f"{BASE_URL}/{year}/{filename}")
    with open(filename, "w") as f:
        f.write(flare_list.content.decode("utf-8"))
    return filename


def burstlist_exists(filename):
    if not os.path.exists(filename):
        return False

    # Get creation time
    f_stats = os.stat(filename)
    b_time = datetime.datetime.fromtimestamp(f_stats.st_ctime)
    now = datetime.datetime.now()

    # if file is older than 6 hours then reload
    age_hrs = (now-b_time).days*24 + (now-b_time).seconds/3600
    if age_hrs >= 6:
        return False

    # No need to download the file
    return True
