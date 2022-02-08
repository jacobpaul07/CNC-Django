# Bosch TimeStamp Format
import dateutil.parser


def timestamp():
    from datetime import datetime
    ts = datetime.now()
    time_zone = ts.astimezone()
    iso_format = time_zone.isoformat(timespec='milliseconds')
    time_stamp = iso_format.replace('+00:00', 'Z')
    return time_stamp


def datetime_parser(json_dict):
    for (key, value) in json_dict.items():
        try:
            matches = ["starttime", "stoptime", "timestamp"]
            if any(str(x).lower() == str(key).lower() for x in matches):
                json_dict[key] = dateutil.parser.parse(value)
        except (ValueError, AttributeError):
            pass
    return json_dict


def float_parser(json_dict):
    for (key, value) in json_dict.items():
        try:
            if isinstance(value, float):
                json_dict[key] = str(value)
        except (ValueError, AttributeError):
            pass
    return json_dict
