from radiospectra.sources import CallistoSpectrogram
import numpy as np
import matplotlib.pyplot as plt
import math
from utils.validation import calculate_snr
import logging
import os
import sys
import tempfile
import multiprocessing
import datetime

class RadioBurstObservation:
    """
    This class serves as a container to hold the extracted spectra
    with metadata.
    """
    def __init__(self) -> None:
        self.instrument = ""
        self.event_time_start = None
        self.event_time_end = None
        self.radio_burst_type = ""
        self.snr = 0.0
        self.spectrum: CallistoSpectrogram = None
        self.__spec_max = 0.0

        # logger is set in method write_observation. See comment there.
        self.__logger = None

    def __prettify(self):
        """
        Applies some error corrections to the spectrogram. Those shall make the
        spectrogram look nicer.
        """
        self.spectrum = self.spectrum.subtract_bg("constbacksub", "elimwrongchannels")
        # self.spectrum = self.spectrum.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1, amount=0.05, change_points=True).denoise()
        # Recalculate the values
        # self.spectrum.elimwrongchannels(overwrite=True)
        self.__spec_max = np.nanmax(self.spectrum.data)
        self.snr = calculate_snr(self.spectrum)

    def reverse_extract_instrument_name(self, instrument_name, include_number=False):
        """
        Convert a lower-case instrument name with underscores to its original hyphenated form.

        Parameters
        ----------
        instrument_name : str
                The instrument name in lower-case with underscores.
        include_number : bool, optional
            Whether to include the last number in the output or not. Default is False.

        Returns
        -------
        str
            The original instrument name with hyphens.
        """
        # Replace underscores with hyphens and upper all the letters
        parts = [part.upper() for part in instrument_name.split("_")]
        if not include_number:
            # Remove the last part if it's a number
            if parts[-1].isnumeric():
                parts.pop()
        # Join the parts with hyphens and return the result
        return "-".join(parts)
        
    def suggest_filename(self) -> str:
        """
        Suggests the file name based on the metadata. This name is chosen according
        to e-Callisto standards 
        """
        instrument_name = self.reverse_extract_instrument_name(self.instrument, include_number=False)
        return f"{instrument_name}_{self.event_time_start.strftime('%Y%m%d')}_{self.event_time_start.strftime('%H%M')}_{self.event_time_end.strftime('%H%M')}"
    
    def create_spectrogram(self, prettify=True):
        self.__logger.debug(f"Create spectrogram for {self.__repr__()}")
        instrument_name = self.instrument # self.reverse_extract_instrument_name(self.instrument, include_number=False)
        self.__logger.debug(instrument_name)
        self.spectrum = CallistoSpectrogram.from_range(
                instrument_name, self.event_time_start, self.event_time_end)
        self.spectrum = self.spectrum.in_interval(self.event_time_start, self.event_time_end)
        self.__spec_max = np.nanmax(self.spectrum.data)
        self.snr = calculate_snr(self.spectrum.data)
        if prettify:
            self.__prettify()
        
        if math.isnan(self.snr):
            self.snr =  -1.0
            self.__logger.info(f"Invalid snr (snr={self.snr}) for {self.instrument} from {self.event_time_start.strftime('%H:%M')} to {self.event_time_end.strftime('%H:%M')}")

        # Adding snr to the fits header for further reference
        self.spectrum.header.append(("snr", self.snr))


    def write_observation(self, connector=None):
        # Because this method is run in multiprocessing env.
        # we must create an individual file handle for it
        self.__logger = logging.getLogger(f'observations_{multiprocessing.current_process().pid}')
        formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s - %(message)s')
        datei_handler = logging.FileHandler(f'logs/observations_{multiprocessing.current_process().pid}_{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.log', 'w+')
        datei_handler.setFormatter(formatter)
        self.__logger.setLevel(logging.INFO)
        self.__logger.addHandler(datei_handler)

        self.create_spectrogram(prettify=True)
        self.__logger.debug(f"Writing for instrument {self.instrument}")
        if self.snr < 0.0:
            self.__logger.info(f"snr undetermined for {self.instrument} - not writing")
            return
        
        plt.ioff()
        fig = plt.figure(figsize=(6,4))
        assert isinstance(self.spectrum, CallistoSpectrogram)
        self.spectrum.plot(fig, vmin=-2, vmax=17, cmap=plt.get_cmap('plasma'))
        fig.tight_layout()

        with tempfile.NamedTemporaryFile() as tmpfile:
            tmp_filename = tmpfile.name
            plt.savefig(f"{tmp_filename}.jpg")
            plt.close(fig)
            self.spectrum.save(f"{tmp_filename}.fit.gz")
            remotename = os.path.join(f"type_{self.radio_burst_type.upper()}", f"{self.suggest_filename()}")
            connector.put_file(remote_name=f"{remotename}.jpg", local_name=f"{tmp_filename}.jpg", overwrite=True)
            connector.put_file(remote_name=f"{remotename}.fit.gz", local_name=f"{tmp_filename}.fit.gz", overwrite=True)
            os.unlink(f"{tmp_filename}.jpg")
            os.unlink(f"{tmp_filename}.fit.gz")

    def __repr__(self) -> str:
        return f"{self.instrument} - {self.event_time_start} - {self.event_time_end}"

