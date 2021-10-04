# Bosch TimeStamp Format
def timestamp():
    from datetime import datetime
    ts = datetime.now()
    time_zone = ts.astimezone()
    iso_format = time_zone.isoformat(timespec='milliseconds')
    time_stamp = iso_format.replace('+05:30', 'Z')
    return time_stamp