from datetime import date, time, datetime


def serialize_date(value: date | None, default: str | date = ""):
    if value is None:
        if isinstance(default, date):
            value = default
        else:
            return default
    return value.isoformat()


def deserialize_date(value: str, default: date | None = None):
    try:
        datetime_value = datetime.fromisoformat(value)
    except ValueError:
        return default
    return datetime_value.date()


def serialize_time(value: time | None, default: str | time = ""):
    if value is None:
        if isinstance(default, time):
            value = default
        else:
            return default
    return value.isoformat(timespec="minutes")


def deserialize_time(value: str, default: time | None = None):
    try:
        datetime_value = datetime.fromisoformat(value)
    except ValueError:
        return default
    return datetime_value.date()


def serialize_datetime(value: datetime | None, default: str | datetime = ""):
    if value is None:
        if isinstance(default, datetime):
            value = default
        else:
            return default
    return value.isoformat(timespec="minutes")


def deserialize_datetime(value: str, default: datetime | None = None):
    try:
        datetime_value = datetime.fromisoformat(value)
    except ValueError:
        return default
    return datetime_value
