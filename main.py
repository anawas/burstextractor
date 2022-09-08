"""
Reads a burst list compiled by C. Monstein from server and processes its data
version 1.2
author: Andreas Wassmer
project: Raumschiff
"""
from radiospectra import __version__
import burstlist
import burstprocessor
import datetime
import logging


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                    filename='app.log', filemode='w',
                    format='%(levelname)s - %(message)s')

    logging.info(f"\n===== Start {datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')} =====\n")
    print(f"\n Radiospectra version = {__version__}\n")
    filename = burstlist.download_burst_list(2022, 9)
    # filename = "e-CALLISTO_debug.txt"
    burst_list = burstlist.process_burst_list(filename)

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
            print("No events found")
    
    logging.info(f"\n===== End {datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')} =====\n")
