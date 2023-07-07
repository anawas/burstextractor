import pytest
import numpy as np
import sys
import datetime
sys.path.insert(0, '..')
import Observation


def test_suggest_filename():
    obs = Observation.RadioBurstObservation()
    obs.instrument = "Arecibo"
    obs.event_time_start = datetime.datetime(2023, 1, 1, 11,0)
    obs.event_time_end = datetime.datetime(2023, 1, 1, 11,30)

    filename = obs.suggest_filename()
    assert filename == "Arecibo_20230101_1100_1130"

