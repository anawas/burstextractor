import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import webdav.WebdavConnector as wdav
import burstlist as bl
import burstprocessor
from bs4 import BeautifulSoup
import urllib3
import logging

BASE_URL = "http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/"

def get_instrument(filename:str) -> str:
    """
    Extracts the instruments name from the FITS filename
    """
    parts = filename.split("_")
    if len(parts) != 4:
        return ""
    return parts[0]
    

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
        instruments_in_service = get_instruments_for_date(ecal_events.iloc[i]["Date"])
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
    burstprocessor.extract_burst(dfc.iloc[i])
