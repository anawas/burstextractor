"""
Reads a burst list compiled by C. Monstein from server and processes its data
version 1.0
author: Andreas Wassmer
project: Raumschiff
"""
import pandas as pd
import requests
import datetime


def download_burst_list(select_year, select_month):
    """
    The burst list contains all (manually) detected radio bursts in per
    month and year. This function gets the file from the server.

    Returns: the filename of the list for further processing
    """
    check_valid_date(select_year, select_month)
    year, month = adjust_year_month(select_year, select_month)

    base_url = (
        f"http://soleil.i4ds.ch/solarradio/data/BurstLists/2010-yyyy_Monstein/{year}/"
    )
    filename = f"e-CALLISTO_{year}_{month}.txt"
    flare_list = requests.get(base_url + filename)
    with open(filename, "w") as f:
        f.write(flare_list.content.decode("utf-8"))
    return filename


def check_valid_date(year, month):
    """
    Check if the argument to the funtion download_burst_list
    is a valid date. If not, aises an exception.
    """
    assert (
        len(str(year)) == 4 and type(year) == int
    ), "First argument year must be a 4-digit integer"
    assert type(month) == int, "Second argument month must be a valid integer"
    assert month >= 1 and month <= 12, "Second argument month must be from 1 to 12"
    if datetime.date.today().year == year:
        assert (
            datetime.date.today().month >= month
        ), "The month {} in {} has not yet occurred".format(month, year)
    assert (
        datetime.date.today().year >= year
    ), "The year {} has not yet occurred".format(year)


def adjust_year_month(year, month):
    """
    We'll work with string numbers in function download_burst_list.
    Here we convert the arguments to strings and pads the month
    to length 2, if necessary.

    Returns: the year and month as strings
    """
    if month < 10:
        m = "0" + str(month)
    else:
        m = str(month)

    return str(year), m


if __name__ == "__main__":
    filename = download_burst_list(2021, 8)
    print(filename)
