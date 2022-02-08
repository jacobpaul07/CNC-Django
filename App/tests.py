def get_duration(duration):

    hours = int(duration / 3600)

    minutes = int(duration % 3600 / 60)

    seconds = int((duration % 3600) % 60)

    raw = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
    formatted = "{:02d}h {:02d}m {:02d}s".format(int(hours), int(minutes), int(seconds))

    return raw, formatted