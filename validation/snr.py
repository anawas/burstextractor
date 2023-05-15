import numpy as np

def calculate_snr(spectrogram):
    """ 
    Calculates the signal to noise ratio of a spectrogram
    """
    signal = np.nanmean(spectrogram)
    noise = np.nanstd(spectrogram)
    return signal/noise