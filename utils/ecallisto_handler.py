from bs4 import BeautifulSoup
import urllib3
import logging
from ecallisto_ng.data_fetching.get_information import get_tables, get_table_names_with_data_between_dates
import datetime

import sys
sys.path.append("/Volumes/VMs/astrophysics/raumschiff/burstextractor")
import burstlist as bl
import burstprocessor
from connectors.defaultconnector import DefaultConnector

BASE_URL = "http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/"

def get_instrument(filename:str) -> str:
    """
    Extracts the instruments name from the FITS filename
    """
    parts = filename.split("_")
    if len(parts) != 4:
        return ""
    return parts[0]
    
def get_instruments_for_date_api(date:str, time:str) -> list:
    t = time.split("-")

    date_time = datetime.datetime.strptime(f"{date} {t[0].strip()}", "%Y%m%d %H:%M")
    start = date_time - datetime.timedelta(minutes=15)
    end = date_time + datetime.timedelta(hours=1)
    return get_table_names_with_data_between_dates(
        start_datetime=start.strftime("%Y-%m-%d %H:%M"),
        end_datetime=end.strftime("%Y-%m-%d %H:%M")
    )
    

def get_instruments_for_date(date:str) -> set:
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

logging.basicConfig(level=logging.INFO,
                filename='ecallistohandler.log', filemode='a',
                format='%(levelname)s - %(message)s')

bursts = bl.process_burst_list("e-CALLISTO_2023_06.txt")

# Extract all datasets with instrument == e-Callisto
ecal_events = bursts.loc[bursts['Instruments'] == "e-Callisto"]
ecal_events.reset_index(drop=True, inplace=True)
print(f"Found {len(ecal_events)} events with e-Callisto instrument")
# Now get all these spectrograms
# First, get all the instruments in service for that day
dfc = ecal_events.copy()
for i in range(len(ecal_events)):
    try:
        instruments_in_service = get_instruments_for_date_api(ecal_events.iloc[i]["Date"], ecal_events.iloc[i]["Time"])
    except urllib3.exceptions.RequestError as e:
        print(f"ERROR -- Could not get instruments for day")
        print(e.url)
    
    print(f"Doing row {i}: Instruments in service: {len(instruments_in_service)}")
    
    n_str = ''
    for index, I in enumerate(instruments_in_service): #enumerate(list) returns (current position, list[current position]) so if we need to know the current position we use enumerate
        if I == "":
            continue
        if index != len(instruments_in_service)-1:
            n_str += str(I) + "," #we don't apply the seperator if we're at the end of the list
        else:
            n_str += str(I)    
    
    dfc.loc[i, "Instruments"] = n_str
    
dfc.to_csv("list.csv", sep="\t", index=False)

for i in range(len(dfc)):
    observations = burstprocessor.extract_radio_burst(dfc.iloc[i])
    for obs in observations:
        try:
            obs.create_spectrogram()
        except BaseException:
            logging.error(f"Could not get spectrogram for {obs.instrument}")
            continue
        obs.write_observation(connector=DefaultConnector())

