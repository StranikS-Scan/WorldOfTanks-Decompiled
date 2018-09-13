# Embedded file name: scripts/client/notification/NotificationsTimeFormatter.py
import time
from time import gmtime
from messenger.formatters import TimeFormatter

class NotificationsTimeFormatter(object):
    DAY_SECONDS = 86400

    def __init__(self):
        super(NotificationsTimeFormatter, self).__init__()

    @classmethod
    def getActualTimeStr(cls, timestamp):
        currentTime = time.time()
        if currentTime - timestamp > cls.DAY_SECONDS or gmtime().tm_mday != gmtime(timestamp).tm_mday:
            return TimeFormatter.getShortDatetimeFormat(timestamp)
        else:
            return TimeFormatter.getShortTimeFormat(timestamp)
