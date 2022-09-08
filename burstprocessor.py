"""
Reads the burst list generate by the burstlist module, downloads the spectrograms
and exstracts the bursts in it.
version 1.3
author: Andreas Wassmer
project: Raumschiff
"""
import matplotlib.pyplot as plt
import numpy as np
from radiospectra.sources import CallistoSpectrogram
import timeutils
import datetime
import logging
import os

BASE_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "../e-Callisto/bursts"))

def prettify(spectro):
    """
    Applies some error corrections to the spectrogram. Those shall make the
    spectrogram look nicer.
    """
    return spectro.elimwrongchannels().subtract_bg().denoise(full=False)


def extract_burst(event):

    start, end = timeutils.extract_and_correct_time(event['Time'])
    start = start - datetime.timedelta(minutes=2)
    if start.minute % 15 == 0:
        start = start + datetime.timedelta(minutes=-1)

    end = end + datetime.timedelta(minutes=2)
    if end.minute % 15 == 0:
        end = end + datetime.timedelta(minutes=1)

    date = str(event['Date'])
    path = os.path.join(BASE_DIR, f"type_{str(event['Type'])}")
    if not os.path.exists(path):
        os.makedirs(path)

    event_start = f"{date[0:4]}/{date[4:6]}/{date[6:8]} {start.hour}:{start.minute}"
    event_end = f"{date[0:4]}/{date[4:6]}/{date[6:8]} {end.hour}:{end.minute}"
    instruments = event['Instruments'].split(',')
    for i in range(len(instruments)):
        instruments[i] = instruments[i].strip()

        # MEXICO-LANCE has got 2 instruments
        if instruments[i] == "MEXICO-LANCE":
            instruments[i] = "MEXICO-LANCE-A"
            instruments.append("MEXICO-LANCE-B")

        # Instrument Malaysia Banting has changed name. Before 2022-07 it was written with 
        # an underscore '_'. After there is a dash '-'. We correct this on the fly
        malaysia_alias = ["Malaysia_Banting", "Malaysia-Banting"]
        if instruments[i] in malaysia_alias:
            if instruments[i].find('_') >= 0:
                new_instr = instruments[i].replace('_', '-')
            else:
                new_instr = instruments[i].replace('-', '_')
            instruments.append(new_instr)

    for instr in instruments:
        # Data from instruments marked with () or [] are either uncertain or messed up.
        # We don't process them
        if not instr.startswith('(') and not instr.startswith('['):

            logging.debug(f"Processing instrument {instr} for event from {event_start} to {event_end}")
            try:
                s = CallistoSpectrogram.from_range(
                    instr, event_start, event_end)
                interesting = s.in_interval(event_start, event_end)

                # the last row in the masked array contains all nan, this we ignore it
                pretty = prettify(interesting)
                spec_max = np.nanmax(pretty.data)
                
                fig = plt.figure(figsize=(6,4))
                pretty.plot(fig, vmin=0, vmax=spec_max*0.6, cmap=plt.get_cmap('plasma'))
                fig.tight_layout()
                
                filename = os.path.join(path, f"{instr}_{event['Date']}_{start.strftime('%H%M')}_{end.strftime('%H%M')}")
                plt.savefig(f"{filename}.jpg")
                plt.close(fig)
                pretty.save(f"{filename}.fit.gz")

            except Exception as e:
                logging.error(f"While processing instrument {instr} for event from {event_start} to {event_end}")
                logging.error("Exception occurred", exc_info=True)
                continue



