"""
The main part of the app
version 1.8
author: Andreas Wassmer
project: Raumschiff
"""
import typer
from radiospectra import __version__
from timeutils import check_valid_date
import burstlist
import burstprocessor
import datetime
import logging
import os
import webdav.WebdavConnector as wdav

def main(year:int = typer.Option(..., help="Observation year"), 
         month:int = typer.Option(..., help="Obervation month"),
         day: int = typer.Option(0, help="Observation day"),
         type:str = typer.Option("all", help="The burst type to process (I to V). If not given, all types are processed."),
         remote:bool = typer.Option(False, help="Write files to raumschiff server.\nNeeds credentials for server access.")
         ):
    
    print(f"\n Radiospectra version = {__version__}\n")

    check_valid_date(year, month, day)
    m = str(month).zfill(2)
    if day > 0:
        d = str(day).zfill(2)

    connector = None
    if remote:
        print("Connect to raumschiff server")
        connector = wdav.WebdavConnector()

    logging.info(f"===== Start {datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')} =====\n")
    logging.info(f"----- Processing data for {year}-{m} -----\n")

    filename = f"e-CALLISTO_{year}_{m}.txt"
    if download_file_needed(filename):
        logging.info("Dowloading burst file")
        filename = burstlist.download_burst_list(year, month)
    else:
        logging.info("Using existing burst file")


    pref_date = None
    if day > 0:
        pref_date = f"{year}{m}{d}"

    burst_list = burstlist.process_burst_list(filename, date=pref_date)

    extract_bursts(burst_list, type, connector=connector)
    logging.info(f"===== End {datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')} =====\n")

def download_file_needed(filename):
    if not os.path.exists(filename):
        return True
    
    # Get creation time
    f_stats = os.stat(filename)
    b_time = datetime.datetime.fromtimestamp(f_stats.st_ctime)
    now = datetime.datetime.now()

    # if file is older than 6 hours then reload
    age_hrs = (now-b_time).days*24 + (now-b_time).seconds/3600 
    if age_hrs >= 6:
        return True

    # No need to download the file
    return False


def extract_bursts(burst_list, chosen_type: str, connector=None):
    # Let's define all burst types that we want to process
    burst_types = ["I", "II", "III", "IV", "V"]    
    types_to_process = list()
    if (chosen_type == "all"):
        types_to_process = burst_types.copy()
    else:
        index = burst_types.index(chosen_type.upper())
        types_to_process.append(burst_types[index])
    
    for type in types_to_process:
        events = burst_list.loc[burst_list["Type"] == type]
        if len(events) > 0:
            print(f"Found {len(events)} event(s) of type {type}")
            for i in range(len(events)):
                row = events.iloc[i]
                try:
                    burstprocessor.extract_burst(row, connector)
                except:
                    logging.error("Cannot process image")
        else:
            print(f"No events of type {type} found")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                    filename='app.log', filemode='a',
                    format='%(levelname)s - %(message)s')

    typer.run(main)
 