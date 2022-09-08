import pytest
from timeutils import extract_and_correct_time, adjust_year_month, check_valid_date

"""
Using fixtures here beacause I think that parametrizing
the tests clutters the code in this case
"""
def test_extractandcorrecttime(event_times):
    for t in event_times:
        start, end = extract_and_correct_time(t)
        assert start.strftime("%H:%M"), end.strftime("%H:%M") == event_times[t]

def test_adjustyearmonth(event_dates):
    for d in event_dates:
        assert adjust_year_month(d[0], d[1]) == event_dates[d]

@pytest.mark.parametrize("year, month", [(2022, 13), (2023, 1), (2022, "12")])
def test_checkvaliddate(year, month):
    with pytest.raises(AssertionError):
        check_valid_date(year, month)