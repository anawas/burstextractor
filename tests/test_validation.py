import pytest
import numpy as np
import sys
sys.path.insert(0, '..')
import validation.snr

def test_validation_for_gauss():
    # Shoud have snr of 5.0
    random_array = np.random.normal(100.0, 20.0, 10000)
    snr = validation.snr.calculate_snr(random_array)
    assert 5.0 == pytest.approx(5.0, 0.001)
