import pytest
import numpy as np
import sys
from radiospectra.sources import CallistoSpectrogram
sys.path.insert(0, '..')
from utils.validation import calculate_snr, has_burst_data

def test_validation_for_gauss():
    # Shoud have snr of 5.0
    random_array = np.random.normal(100.0, 20.0, 10000)
    snr = calculate_snr(random_array)
    assert 5.0 == pytest.approx(5.0, 0.001)


def test_burst_detection():
    valid_spec = CallistoSpectrogram.read("resources/ALASKA_HAARP_VALID.fit.gz")
    invalid_spec = CallistoSpectrogram.read("resources/ALASKA_HAARP_VALID.fit.gz")
