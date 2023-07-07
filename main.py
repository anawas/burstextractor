"""
The main part of the app
version 1.8
author: Andreas Wassmer
project: Raumschiff
"""
import typer
from radiospectra import __version__
import utils.timeutils
import burstlist
import burstprocessor
import datetime
import logging
import os
import webdav.WebdavConnector as wdav
import multiprocessing

def main(year:int = typer.Option(..., help="Observation year"), 
         month:int = typer.Option(..., help="Obervation month"),
         day: int = typer.Option(0, help="Observation day"),
         type:str = typer.Option("all", help="The burst type to process (I to V). If not given, all types are processed."),
         remote:bool = typer.Option(False, help="Write files to raumschiff server.\nNeeds credentials for server access.")
         ):
    
    print(f"\n Radiospectra version = {__version__}\n")

    utils.timeutils.check_valid_date(year, month, day)
    year, m, d = utils.timeutils.adjust_year_month_day(year, month, day)

    connector = None
    if remote:
        print("Connect to raumschiff server")
        connector = wdav.WebdavConnector()

    logging.info(f"===== Start {datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')} =====\n")
    logging.info(f"----- Processing data for {year}-{m} -----\n")

    filename = f"e-CALLISTO_{year}_{m}.txt"
    filename = burstlist.download_burst_list(year, month)

    pref_date = None
    if day > 0:
        pref_date = f"{year}{m}{d}"

    burst_list = burstlist.process_burst_list(filename, date=pref_date)
    observations = extract_bursts(burst_list, type, connector=connector)
    processes = []
    if len(observations) > 0:
        for obs in observations:
            obs.create_spectrogram()
            p = multiprocessing.Process(target=obs.create_spectrogram)
            p.start()
            processes.append(p)
    for p in processes:
        p.join()
    
    for obs in observations:
        obs.write_observation()


    logging.info(f"===== End {datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')} =====\n")



def extract_bursts(burst_list, chosen_type: str, connector=None):
    # Let's define all burst types that we want to process
    burst_types = ["I", "II", "III", "IV", "V"]    
    types_to_process = list()
    if (chosen_type == "all"):
        types_to_process = burst_types.copy()
    else:
        index = burst_types.index(chosen_type.upper())
        types_to_process.append(burst_types[index])
    
    observation = list()
    for type in types_to_process:
        events = burst_list.loc[burst_list["Type"] == type]
        if len(events) > 0:
            print(f"Found {len(events)} event(s) of type {type}")
            for i in range(len(events)):
                row = events.iloc[i]
                try:
                    observation += burstprocessor.extract_radio_burst(row, connector)
                except BaseException as e:
                    logging.error(f"Cannot process image\n{e.args}")
                    
        else:
            print(f"No events of type {type} found")
    return observation

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                    filename='app.log', filemode='a',
                    format='%(asctime)s:%(name)s:%(levelname)s - %(message)s')

    typer.run(main)
 