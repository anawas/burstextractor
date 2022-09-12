"""
The main part of the app
version 1.0
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

def fix_month_length(month):
    if month < 10:
        m = "0" + str(month)
    else:
        m = str(month)
    return m

def main(year:int = typer.Option(..., help="Observation year"), 
         month:int = typer.Option(..., help="Obervation month"),
         type:str = typer.Option("all", help="The burst type to process (I to V). If not given, all types are processed.")):
    
    check_valid_date(year, month)
    m = fix_month_length(month)

    logging.info(f"===== Start {datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')} =====\n")
    logging.info(f"----- Processing data for {year}-{m} -----\n")

    filename = f"e-CALLISTO_{year}_{m}.txt"
    if not os.path.exists(filename):
        filename = burstlist.download_burst_list(year, month)

    burst_list = burstlist.process_burst_list(filename)
    extract_bursts(burst_list, type)
    logging.info(f"===== End {datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')} =====\n")

def extract_bursts(burst_list, chosen_type: str):
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
                burstprocessor.extract_burst(row)
        else:
            print(f"No events of type {type} found")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                    filename='app.log', filemode='a',
                    format='%(levelname)s - %(message)s')

    print(f"\n Radiospectra version = {__version__}\n")
    typer.run(main)
 