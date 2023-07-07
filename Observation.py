from radiospectra.sources import CallistoSpectrogram
import numpy as np
import matplotlib.pyplot as plt
import math
from validation import snr
import logging
import os
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

        self.__logger = logging.getLogger(__name__)
        self.__set_logger()

    def __set_logger(self):
        """
        Define logging for this class
        """
        formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s - %(message)s')
        datei_handler = logging.FileHandler('observations.log', 'w')
        datei_handler.setFormatter(formatter)
        self.__logger.addHandler(datei_handler)
        self.__logger.setLevel(logging.DEBUG)

    def __prettify(self):
        """
        Applies some error corrections to the spectrogram. Those shall make the
        spectrogram look nicer.
        """
        self.spectrum = self.spectrum.subtract_bg("constbacksub", "elimwrongchannels") 
        self.spectrum = self.spectrum.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1, amount=0.05, change_points=True).denoise()
        
    def suggest_filename(self) -> str:
        """
        Suggests the file name based on the metadata. This name is chosen according
        to e-Callisto standards 
        """
        return f"{self.instrument}_{self.event_time_start.strftime('%Y%m%d')}_{self.event_time_start.strftime('%H%M')}_{self.event_time_end.strftime('%H%M')}"
    
    def create_spectrogram(self):
        self.spectrum = CallistoSpectrogram.from_range(
                self.instrument, self.event_time_start, self.event_time_end)
        self.spectrum = self.spectrum.in_interval(self.event_time_start, self.event_time_end)
                
        self.__prettify()
        self.__spec_max = np.nanmax(self.spectrum.data)
        self.snr = snr.calculate_snr(self.spectrum.data)
        if math.isnan(self.snr):
            self.snr =  -1.0
            self.__logger.info(f"Invalid snr (snr={self.snr}) for {self.instrument} from {self.event_time_start.strftime('%H:%M')} to {self.event_time_end.strftime('%H:%M')}")

        # Adding snr to the fits header for further reference
        self.spectrum.header.append(("snr", self.snr))

    def write_observation(self, connector=None):
        filename = os.path.join(".", self.suggest_filename())
        print(f"Writing for instrument {self.instrument}")
        if self.snr < 0.0:
            self.__logger.info("snr undetermined - not writing")
            return
        
        plt.ioff()
        fig = plt.figure(figsize=(6,4))
        assert isinstance(self.spectrum, CallistoSpectrogram)
        self.spectrum.plot(fig, vmin=0, vmax=self.__spec_max*0.6, cmap=plt.get_cmap('plasma'))
        fig.tight_layout()

        if connector is None:
            plt.savefig(f"{filename}.jpg")
            plt.close(fig)
            self.spectrum.save(f"{filename}.fit.gz")
        else:
            self.__logger.error("Connector not supported yet")

    def __repr__(self) -> str:
        return f"{self.instrument} - {self.event_time_start} - {self.event_time_end}"

