import datetime


def extract_and_correct_time(event_time):
    """
    the event time may have typos in it, i.e. 01_55 instead of 01:55.
    this function corrects it.
    Returns: start and end of event as datetime object
    May seems overkill but we never now what we will do with it.
    """
    start = event_time.split("-")[0]
    end = event_time.split("-")[1]

    if ":" not in start:
        start = start[0:2] + ":" + start[3:-1]

    if ":" not in end:
        end = end[0:2] + ":" + end[3:-1]

    return datetime.datetime.strptime(start, "%H:%M"), datetime.datetime.strptime(end, "%H:%M")


def check_valid_date(year, month):
    """
    Check if the argument to the funtion download_burst_list
    is a valid date. If not, aises an exception.
    """
    assert (
        len(str(year)) == 4 and type(year) == int
    ), "First argument year must be a 4-digit integer"
    assert type(month) == int, "Second argument month must be a valid integer"
    assert month >= 1 and month <= 12, "Second argument month must be from 1 to 12"
    if datetime.date.today().year == year:
        assert (
            datetime.date.today().month >= month
        ), "The month {} in {} has not yet occurred".format(month, year)
    assert (
        datetime.date.today().year >= year
    ), "The year {} has not yet occurred".format(year)


def adjust_year_month(year, month):
    """
    We'll work with string numbers in function download_burst_list.
    Here we convert the arguments to strings and pads the month
    to length 2, if necessary.

    Returns: the year and month as strings
    """
    if month < 10:
        m = "0" + str(month)
    else:
        m = str(month)

    return str(year), m
