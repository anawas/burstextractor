import pytest

"""
Using fixtures here beacause I think that parametrizing
the tests clutters the code in this case
"""
@pytest.fixture()
def event_times():
    times = {}
    times["12:55-12:56"] = ("12:55", "12:56")
    times["12_55-12:56"] = ("12:55", "12:56")
    times["12.55-12_56"] = ("12:55", "12:56")
    times["12.55-12:56"] = ("12:55", "12:56")

    return times

@pytest.fixture()
def event_dates():
    dates = {}
    dates[(2022, 2)] = ("2022", "02")
    dates[(2012, 12)] = ("2012", "12")

    return dates
