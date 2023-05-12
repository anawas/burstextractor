import pytest
from timeutils import extract_and_correct_time, adjust_year_month, check_valid_date


def test_extractandcorrecttime(event_times):
    """
    Using fixtures here beacause I think that parametrizing
    the tests clutters the code in this case
    """    
    for t in event_times:
        start, end = extract_and_correct_time(t)
        assert start.strftime("%H:%M"), end.strftime("%H:%M") == event_times[t]

def test_adjustyearmonth(event_dates):
    for d in event_dates:
        assert adjust_year_month(d[0], d[1]) == event_dates[d]

@pytest.mark.parametrize("year, month, day", [(2024, 3, 1), (2022, 13, 1), (2023, 1, 41), (2022, "12", 1)])
def test_checkvaliddate(year, month, day):
    with pytest.raises(AssertionError):
        check_valid_date(year, month, day)