"""
Reads a burst list compiled by C. Monstein from server and processes its data
version 1.3
author: Andreas Wassmer
project: Raumschiff
"""
import pandas as pd
import utils.timeutils
import requests

BASE_URL = f"http://soleil.i4ds.ch/solarradio/data/BurstLists/2010-yyyy_Monstein"
    
def process_burst_list(filename, date=None) -> pd.DataFrame:
    """
    Let's discard the entries with missing data.
    These events have a time stamp of "##:##-##:##" with no further data in the row except the date
    I like to use a conditional for filtering. I think the filter is more readable.
    Especially if there are several conditions
    If the user wants the data of a specific day this data is extracted as well 

    Returns: A Pandas Dataframe with valid events
    """
    col_names = ['Date', 'Time', 'Type', 'Instruments']
    data = pd.read_csv(filename, sep="\t", skiprows=8, skipfooter=4,
                       index_col=False, encoding="latin-1", names=col_names, engine="python")

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
    month and year. This function gets the file from the server.

    Returns: the filename of the list.
             I decided not to return the content but rather the
             location of the file. This keeps the data for further
             processing with other tools if needed.
    """
    # Check for valid date has been done in main
    # timeutils.check_valid_date(select_year, select_month)
    year, month = utils.timeutils.adjust_year_month(select_year, select_month)

    filename = f"e-CALLISTO_{year}_{month}.txt"
    flare_list = requests.get(f"{BASE_URL}/{year}/{filename}")
    with open(filename, "w") as f:
        f.write(flare_list.content.decode("utf-8"))
    return filename
