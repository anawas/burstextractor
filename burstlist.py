"""
Reads a burst list compiled by C. Monstein from server and processes its data
version 1.0
author: Andreas Wassmer
project: Raumschiff
"""
import matplotlib.pyplot as plt
import pandas as pd
from radiospectra.sources.callisto import CallistoSpectrogram
import requests
import datetime


def process_burst_list(filename):
    col_names = ['Date', 'Time', 'Type', 'Instruments']
    data = pd.read_csv(filename, sep="\t", skiprows=8, skipfooter=4,
                       index_col=False, encoding="latin-1", names=col_names, engine="python")

    # let's discard the entries with missing data
    # these events have a time stamp of "##:##-##:##" with no further data in the row except the date
    # I like to use a conditional for filtering. I think the filter is more readable.
    # Especially if there are several conditions
    missing_conditional = data['Time'] != "##:##-##:##"
    cleaned = data.loc[missing_conditional]
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


def extract_and_correct_time(event_time):
    """
    the event time may have typos in it, e.g. 01_55 instead of 01:55.
    this function corrects it.
    Returns: start and end of event as datetime object
    May seems overkill but we never now what we will do with it.
    """
    start = event_time.split("-")[0]
    end = event_time.split("-")[1]

    if ":" not in start:
        start = start[0:2] + ":" + start[3:-1]

    if ":" not in end:
        end = end[0:2] + ":" + end[3:-1]

    return datetime.datetime.strptime(start, "%H:%M"), datetime.datetime.strptime(end, "%H:%M")


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


def print_row(row):
    print(f"Instrument: {row['Instruments']}")
    print(f"Event time: {row['Time']}")


if __name__ == "__main__":
    filename = download_burst_list(2022, 8)
    burst_list = process_burst_list(filename)

    # Let's get all type III bursts
    type_3 = burst_list.loc[burst_list["Type"] == "III"]
    row = type_3.iloc[3]
    print_row(row)
    start, end = extract_and_correct_time(row['Time'])
    start = start - datetime.timedelta(minutes=2)
    end = end + datetime.timedelta(minutes=2)
    print(f"{end-start}")

    date = str(row['Date'])
    event_start = f"{date[0:4]}/{date[4:6]}/{date[6:8]} {start.hour}:{start.minute}"
    event_end = f"{date[0:4]}/{date[4:6]}/{date[6:8]} {end.hour}:{end.minute}"
    instruments = row['Instruments'].split(',')
    for i in range(len(instruments)):
        instruments[i] = instruments[i].strip()
        # MEXICO-LANCE has got 2 instruments
        if instruments[i] == "MEXICO-LANCE":
            instruments[i] = "MEXICO-LANCE-A"
            instruments.append("MEXICO-LANCE-B")

    for instr in instruments:
        if not instr.startswith('('):
            try:
                s = CallistoSpectrogram.from_range(
                    instr, event_start, event_end)
                s = s.subtract_bg()
                intresting = s.in_interval(event_start, event_end)
                intresting.peek(vmin=0, vmax=5)
            except:
                print(f"ERROR loading instrument {instr}")
                continue
