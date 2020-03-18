from datetime import timedelta, timezone


class DateTime:
    def __init__(self, dt, time_zone='UTC'):
        self.dt = dt
        if time_zone == 'KST':
            self.dt = self.dt + timedelta(hours=9)

    def time_stamp(self):
        return int(self.dt.replace(tzinfo=timezone.utc).timestamp())

    def utc_str(self):
        return self.dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

    def localtime_str(self):
        return '{0:%Y-%m-%d %H:%M:%S}'.format(self.dt)
