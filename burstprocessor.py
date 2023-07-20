"""
Reads the burst list generated by the burstlist module, downloads the spectrograms
and exstracts the bursts in it.
version 1.7
author: Andreas Wassmer
project: Raumschiff
"""
import matplotlib.pyplot as plt
import numpy as np
from radiospectra.sources import CallistoSpectrogram
import connectors.WebdavConnector as wdav
import tempfile
import utils.timeutils
import datetime
import logging
import os
from utils.validation import calculate_snr
from Observation import RadioBurstObservation

BASE_DIR = "temp/" # eCallisto/bursts"

def prettify(spectro):
    """
    Applies some error corrections to the spectrogram. Those shall make the
    spectrogram look nicer.
    """
    no_bg = spectro.subtract_bg("constbacksub", "elimwrongchannels") 
    return no_bg.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1,
                                     amount=0.05, change_points=True).denoise()

def extract_radio_burst(event, connector:wdav.WebdavConnector=None) -> list:
    # There may be a typo in the event time. If so the time cannot be parsed.
    # We raise an exception, report it in the log an return without processing.
    try:
        start, end = utils.timeutils.extract_and_correct_time(event['Time'])
    except Exception as ex:
        logging.error(f"While processing event {event['Time']} ")
        logging.error("Exception occurred", exc_info=False)
        return

    start = start - datetime.timedelta(minutes=2)
    if start.minute % 15 == 0:
        start = start + datetime.timedelta(minutes=-1)

    end = end + datetime.timedelta(minutes=2)
    if end.minute % 15 == 0:
        end = end + datetime.timedelta(minutes=1)

    date = str(event['Date'])
    path = os.path.join(BASE_DIR, f"type_{str(event['Type'])}")

    if connector is None:
        if not os.path.exists(path):
            os.makedirs(path)
    else:
        if not connector.check_dir_exists(path):
            print(f"Creating {path}")
            connector.make_dir(path)


    event_start_str = f"{date[0:4]}/{date[4:6]}/{date[6:8]} {start.hour}:{start.minute}"
    event_start = datetime.datetime.strptime(event_start_str, "%Y/%m/%d %H:%M")
    event_end_str = f"{date[0:4]}/{date[4:6]}/{date[6:8]} {end.hour}:{end.minute}"
    event_end = datetime.datetime.strptime(event_end_str, "%Y/%m/%d %H:%M")
    instruments = event['Instruments'].split(',')
    for i in range(len(instruments)):
        instruments[i] = instruments[i].strip()

        # MEXICO-LANCE has got 2 instruments
        if instruments[i] == "MEXICO-LANCE":
            instruments[i] = "MEXICO-LANCE-A"
            instruments.append("MEXICO-LANCE-B")

        # Instrument Malaysia Banting has changed name. Before 2022-07 it was written with 
        # an underscore '_'. After that there is a dash '-'. We correct this on the fly
        malaysia_alias = ["Malaysia_Banting", "Malaysia-Banting"]
        if instruments[i] in malaysia_alias:
            if instruments[i].find('_') >= 0:
                new_instr = instruments[i].replace('_', '-')
            else:
                new_instr = instruments[i].replace('-', '_')
            instruments.append(new_instr)
        
        # Instrument name "e-Callisto" means that there are too many stations to report or, 
        # PI on vacation or out of office
        # We skip those entries
        if instruments[i] == "e-Callisto":
            instruments.remove(instruments[i])
    
    observation_list = list()
    
    for instr in instruments:
        # Data from instruments marked with () or [] are either uncertain or messed up.
        # We don't process them
        if not instr.startswith('(') and not instr.startswith('['):

            logging.debug(f"Processing instrument {instr} for event from {event_start} to {event_end}")
            try:
                obs = RadioBurstObservation()
                obs.instrument = instr
                obs.event_time_start = event_start
                obs.event_time_end = event_end
                obs.radio_burst_type = str(event['Type'])
                observation_list.append(obs)
                """
                s = CallistoSpectrogram.from_range(
                    instr, event_start, event_end)
                interesting = s.in_interval(event_start, event_end)
                
                # the last row in the masked array contains all nan, this we ignore it
                pretty = prettify(interesting)
                spec_max = np.nanmax(pretty.data)
                quality = snr.calculate_snr(pretty.data)
                logging.debug(f"{instr} snr: {quality}")

                # Adding snr to the fits header for further reference
                pretty.header.append(("snr", quality))
                plt.ioff()
                fig = plt.figure(figsize=(6,4))
                pretty.plot(fig, vmin=0, vmax=spec_max*0.6, cmap=plt.get_cmap('plasma'))
                fig.tight_layout()
                
                filename = os.path.join(path, f"{instr}_{event['Date']}_{start.strftime('%H%M')}_{end.strftime('%H%M')}")
                if connector is None:
                    plt.savefig(f"{filename}.jpg")
                    plt.close(fig)
                    pretty.save(f"{filename}.fit.gz")
                else:
                    print("Writing files to server")
                    with tempfile.TemporaryDirectory() as tmpdir:
                        tmpfile = tempfile.NamedTemporaryFile(mode="w")
                        tmpfile.close()
                        tmp_filename = os.path.join(tmpdir, tmpfile.name)
                        plt.savefig(f"{tmp_filename}.jpg")
                        plt.close(fig)
                        pretty.save(f"{tmp_filename}.fit.gz")
                        
                    filename = os.path.join(path, f"{instr}_{event['Date']}_{start.strftime('%H%M')}_{end.strftime('%H%M')}")
                    connector.put_file(remote_name=f"{filename}.jpg", local_name=f"{tmp_filename}.jpg", overwrite=False)
                    connector.put_file(remote_name=f"{filename}.fit.gz", local_name=f"{tmp_filename}.fit.gz", overwrite=False)
                    """
            except ValueError:
                logging.error(f"No data for instrument {instr} on {event['Date']} at {start.strftime('%H:%M')} to {end.strftime('%H:%M')}")
            except BaseException as e:
                logging.error(f"While processing instrument {instr} for event from {event_start} to {event_end}")
                logging.error("Exception occurred", exc_info=True)
                continue
    return observation_list


