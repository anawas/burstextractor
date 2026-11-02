import datetime

from observation import Observation


def test_suggest_filename():
    obs = Observation.RadioBurstObservation()
    obs.instrument = "Arecibo"
    obs.event_time_start = datetime.datetime(2023, 1, 1, 11, 0)
    obs.event_time_end = datetime.datetime(2023, 1, 1, 11, 30)

    filename = obs.suggest_filename()
    # suggest_filename normalises the instrument to the upper-case e-Callisto form
    assert filename == "ARECIBO_20230101_1100_1130"


def test_suggest_filename_strips_underscores_and_number():
    obs = Observation.RadioBurstObservation()
    obs.instrument = "alaska_cohoe_62"
    obs.event_time_start = datetime.datetime(2023, 1, 1, 11, 0)
    obs.event_time_end = datetime.datetime(2023, 1, 1, 11, 30)

    assert obs.suggest_filename() == "ALASKA-COHOE_20230101_1100_1130"
