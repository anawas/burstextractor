import datetime


def extract_and_correct_time(event_time):
    """
    the event time may have typos in it, i.e. 01_55 instead of 01:55.
    this function corrects it.
    Returns: start and end of event as datetime object
    May seems overkill but we never now what we will do with it.
    """
    try:
        start = event_time.split("-")[0]
        end = event_time.split("-")[1]
    except Exception as ex:
        raise ex

    if ":" not in start:
        start = start[0:2] + ":" + start[3:-1]

    if ":" not in end:
        end = end[0:2] + ":" + end[3:-1]

    return datetime.datetime.strptime(start, "%H:%M"), datetime.datetime.strptime(end, "%H:%M")


def check_valid_date(year, month, day):
    """
    Check if the argument to the funtion download_burst_list
    is a valid date. If not, aises an exception.
    """
    days_per_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    assert (
        len(str(year)) == 4 and type(year) is int
    ), "First argument year must be a 4-digit integer"
    assert type(month) is int, "Second argument month must be a valid integer"
    assert month >= 1 and month <= 12, "Second argument month must be from 1 to 12"
    assert day <= days_per_month[month], f"Month given has only {days_per_month[month]} days"
    if datetime.date.today().year == year:
        assert (
            datetime.date.today().month >= month
        ), "Month {} in {} lies in the future".format(month, year)
    assert (
        datetime.date.today().year >= year
    ), "The year {} lies in the future".format(year)


def adjust_year_month_day(year, month, day=None):
    """
    We'll work with string numbers in function download_burst_list.
    Here we convert the arguments to strings and pads the month
    to length 2, if necessary.

    Returns: the year, month and day as strings with leading 0
    """
    m = str(month).zfill(2)

    if day is not None:
        d = str(day).zfill(2)
    else:
        d = ""

    return str(year), m, d
