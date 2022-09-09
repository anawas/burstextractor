"""
The main part of the app
version 1.0
author: Andreas Wassmer
project: Raumschiff
"""
from radiospectra import __version__
import burstlist
import burstprocessor
import datetime
import logging

def extract_bursts(burst_list):
        # Let's define all burst types that we want to process
    burst_types = ["I", "II", "III", "IV", "V"]
    for type in burst_types:
        events = burst_list.loc[burst_list["Type"] == type]
        if len(events) > 0:
            print(f"Found {len(events)} event(s)")
            for i in range(len(events)):
                row = events.iloc[i]
                burstprocessor.extract_burst(row)
        else:
            print(f"No events of type {type} found")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                    filename='app.log', filemode='w',
                    format='%(levelname)s - %(message)s')

    logging.info(f"\n===== Start {datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')} =====\n")
    print(f"\n Radiospectra version = {__version__}\n")
    for month in range (5,10):
        # filename = burstlist.download_burst_list(2022, month)
        if month < 10:
            m = "0" + str(month)
        else:
            m = str(month)
        
        logging.info(f"\n----- Processing month {m} -----\n")
        filename = f"e-CALLISTO_2022_{m}.txt"
        burst_list = burstlist.process_burst_list(filename)
        extract_bursts(burst_list)
    
    logging.info(f"\n===== End {datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')} =====\n")
 