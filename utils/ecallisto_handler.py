import datetime
import logging

import urllib3
from bs4 import BeautifulSoup
from ecallisto_ng.data_fetching.get_information import (
    get_table_names_with_data_between_dates)

from burstprocessing import burstlist as bl
from burstprocessing import burstprocessor
from connectors.defaultconnector import DefaultConnector

BASE_URL = "http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/"


def get_instrument(filename: str) -> str:
    """
    Extracts the instruments name from the FITS filename
    """
    parts = filename.split("_")
    if len(parts) != 4:
        return ""
    return parts[0]


def get_instruments_for_date_api(date: str, time: str) -> list:
    t = time.split("-")

    date_time = datetime.datetime.strptime(f"{date} {t[0].strip()}", "%Y%m%d %H:%M")
    start = date_time - datetime.timedelta(minutes=15)
    end = date_time + datetime.timedelta(hours=1)
    return get_table_names_with_data_between_dates(
        start_datetime=start.strftime("%Y-%m-%d %H:%M"),
        end_datetime=end.strftime("%Y-%m-%d %H:%M")
    )


def get_instruments_for_date(date: str) -> set:
    """
    Gets all the instruments that reported on that date
    """
    instruments = set()

    http = urllib3.PoolManager()

    url = f"{BASE_URL}{date[0:4]}/{date[4:6]}/{date[6:8]}"
    resp = http.request("GET", url)
    if resp.status != 200:
        raise urllib3.exceptions.RequestError(http, url, None)

    page = resp.data

    html = BeautifulSoup(page, "html.parser")
    table_entries = html.find_all("a")
    for entry in table_entries:
        t = get_instrument(entry["href"])
        instruments.add(t)
    return instruments


def get_ecallisto_events(burst_list_file: str):
    """
    Extracts all datasets with instrument == e-Callisto from the burst list
    """
    bursts = bl.process_burst_list(burst_list_file)

    ecal_events = bursts.loc[bursts['Instruments'] == "e-Callisto"]
    ecal_events.reset_index(drop=True, inplace=True)
    print(f"Found {len(ecal_events)} events with e-Callisto instrument")
    return ecal_events


def resolve_instruments_in_service(ecal_events):
    """
    Replaces the generic "e-Callisto" instrument of every event with the
    instruments that were in service at the time of the event.

    Returns: a copy of the events with the "Instruments" column filled in
    """
    dfc = ecal_events.copy()
    for i in range(len(ecal_events)):
        try:
            instruments_in_service = get_instruments_for_date_api(ecal_events.iloc[i]["Date"], ecal_events.iloc[i]["Time"])
        except urllib3.exceptions.RequestError as e:
            # Leave this row's instrument as it is and move on. Without the
            # continue we would reuse the previous row's instruments.
            logging.error(f"Could not get instruments for row {i}: {e.url}")
            print(f"ERROR -- Could not get instruments for row {i}, skipping")
            print(e.url)
            continue

        print(f"Doing row {i}: Instruments in service: {len(instruments_in_service)}")

        # join() puts the separator between the entries only, so we don't have
        # to track where the end of the list is. Empty entries are dropped
        # first, otherwise they would leave a separator behind.
        dfc.loc[i, "Instruments"] = ",".join(str(I) for I in instruments_in_service if I != "")

    return dfc


def write_spectrograms(dfc, connector=None):
    """
    Creates and writes the spectrogram of every event in the list
    """
    if connector is None:
        connector = DefaultConnector()

    for i in range(len(dfc)):
        observations = burstprocessor.extract_radio_burst(dfc.iloc[i])
        for obs in observations:
            try:
                obs.create_spectrogram()
            except BaseException:
                logging.error(f"Could not get spectrogram for {obs.instrument}")
                continue
            obs.write_observation(connector=connector)


def main(burst_list_file: str = "e-CALLISTO_2023_06.txt"):
    ecal_events = get_ecallisto_events(burst_list_file)

    # Now get all these spectrograms
    # First, get all the instruments in service for that day
    dfc = resolve_instruments_in_service(ecal_events)
    dfc.to_csv("list.csv", sep="\t", index=False)

    write_spectrograms(dfc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        filename='ecallistohandler.log', filemode='a',
                        format='%(levelname)s - %(message)s')

    main()
