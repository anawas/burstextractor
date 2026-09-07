import sys

import numpy as np
import pytest

sys.path.insert(0, '..')
from utils.validation import calculate_snr


def test_validation_for_gauss():
    # mean 100 / std 20 should have an snr of 5.0. Seeded and with a large
    # sample so the sampling error stays well inside the tolerance.
    rng = np.random.default_rng(42)
    random_array = rng.normal(100.0, 20.0, 1_000_000)
    snr = calculate_snr(random_array)
    assert snr == pytest.approx(5.0, rel=0.01)


def test_validation_ignores_nans_in_2d_data():
    # calculate_snr takes the raw spectrogram data, which is 2d and may hold NaNs
    data = np.array([[1.0, 3.0, np.nan], [np.nan, 5.0, 7.0]])
    assert calculate_snr(data) == pytest.approx(np.mean([1.0, 3.0, 5.0, 7.0]) / np.std([1.0, 3.0, 5.0, 7.0]))


def test_burst_detection():
    # these tests must be written
    # valid_spec = CallistoSpectrogram.read("resources/ALASKA_HAARP_VALID.fit.gz")
    # invalid_spec = CallistoSpectrogram.read("resources/ALASKA_HAARP_VALID.fit.gz")
    pass
