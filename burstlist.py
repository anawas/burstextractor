"""
Reads a burst list compiled by C. Monstein from server and processes its data
version 1.0
author: Andreas Wassmer
project: Raumschiff
"""
import matplotlib.pyplot as plt
import pandas as pd
from radiospectra.sources.callisto import CallistoSpectrogram
from radiospectra import __version__
import timeutils
import requests
import datetime
import logging

logging.basicConfig(level=logging.DEBUG,
                    filename='app.log', filemode='w',
                    format='%(levelname)s - %(message)s')


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
    timeutils.check_valid_date(select_year, select_month)
    year, month = timeutils.adjust_year_month(select_year, select_month)

    base_url = (
        f"http://soleil.i4ds.ch/solarradio/data/BurstLists/2010-yyyy_Monstein/{year}/"
    )
    filename = f"e-CALLISTO_{year}_{month}.txt"
    flare_list = requests.get(base_url + filename)
    with open(filename, "w") as f:
        f.write(flare_list.content.decode("utf-8"))
    return filename

def prettify(spectro):
    """
    Applies some error corrections to the spectrogram. Those shall make the
    spectrogram look nicer.
    """
    return spectro.elimwrongchannels().subtract_bg().denoise(full=True)


def extract_burst(event):
    start, end = timeutils.extract_and_correct_time(event['Time'])
    start = start - datetime.timedelta(minutes=2)
    end = end + datetime.timedelta(minutes=2)

    date = str(event['Date'])
    event_start = f"{date[0:4]}/{date[4:6]}/{date[6:8]} {start.hour}:{start.minute}"
    event_end = f"{date[0:4]}/{date[4:6]}/{date[6:8]} {end.hour}:{end.minute}"
    instruments = event['Instruments'].split(',')
    for i in range(len(instruments)):
        instruments[i] = instruments[i].strip()

        # MEXICO-LANCE has got 2 instruments
        if instruments[i] == "MEXICO-LANCE":
            instruments[i] = "MEXICO-LANCE-A"
            instruments.append("MEXICO-LANCE-B")

    for instr in instruments:
        if not instr.startswith('('):
            logging.debug(f"Processing instrument {instr}")
            try:
                s = CallistoSpectrogram.from_range(
                    instr, event_start, event_end)
                s = s.subtract_bg()
                # interesting = s.in_interval(event_start, event_end)
                spec_mean = s.data.mean()
                min = -5*spec_mean
                max = 20*spec_mean

                if min > max:
                    min *= -1
                    max *= -1

                prettify(s).save(f"{instr}-{event['Date']}-{start.strftime('%H%M')}-{end.strftime('%H%M')}.fit.gz")
                #s.peek(vmin=min, vmax=max)

            except Exception as e:
                logging.error("Exception occurred", exc_info=True)
                continue


def print_row(row):
    print(f"Instrument: {row['Instruments']}")
    print(f"Event time: {row['Time']}")


if __name__ == "__main__":

    print(f"\n Radiospectra version = {__version__}\n")
    filename = download_burst_list(2022, 8)
    burst_list = process_burst_list(filename)

    # Let's get all type IV bursts
    events = burst_list.loc[burst_list["Type"] == "III"]
    if len(events) > 0:
        print(f"Found {len(events)} event(s)")
        for i in range(len(events)):
            row = events.iloc[i]
            extract_burst(row)
    else:
        print("No events found")
