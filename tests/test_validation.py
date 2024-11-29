import sys

import numpy as np
import pytest

sys.path.insert(0, '..')
from utils.validation import calculate_snr


def test_validation_for_gauss():
    # Shoud have snr of 5.0
    random_array = np.random.normal(100.0, 20.0, 10000)
    snr = calculate_snr(random_array)
    assert 5.0 == pytest.approx(snr, 0.001)


def test_burst_detection():
    # these tests must be written
    # valid_spec = CallistoSpectrogram.read("resources/ALASKA_HAARP_VALID.fit.gz")
    # invalid_spec = CallistoSpectrogram.read("resources/ALASKA_HAARP_VALID.fit.gz")
    pass
