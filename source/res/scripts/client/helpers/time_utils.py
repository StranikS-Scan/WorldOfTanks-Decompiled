# Embedded file name: scripts/client/helpers/time_utils.py
import time
import BigWorld
import datetime
import calendar
from debug_utils import *
from helpers import i18n
ONE_MINUTE = 60
ONE_HOUR = 60 * ONE_MINUTE
ONE_DAY = 24 * ONE_HOUR
HALF_YEAR = 183 * ONE_DAY

class _TimeCorrector(object):

    def __init__(self):
        self._evalTimeCorrection(time.time())

    def _evalTimeCorrection(self, serverUTCTime):
        self.__clientLoginTime = BigWorld.time()
        self.__serverLoginUTCTime = serverUTCTime

    def __loginDelta(self):
        return BigWorld.time() - self.__clientLoginTime

    timeCorrection = property(lambda self: self.serverUTCTime - time.time())
    serverUTCTime = property(lambda self: self.__serverLoginUTCTime + self.__loginDelta())

    @property
    def serverRegionalTime(self):
        regionalSecondsOffset = 0
        try:
            serverRegionalSettings = BigWorld.player().serverSettings['regional_settings']
            regionalSecondsOffset = serverRegionalSettings['starting_time_of_a_new_day']
        except Exception:
            LOG_CURRENT_EXCEPTION()

        return _g_instance.serverUTCTime + regionalSecondsOffset


_g_instance = _TimeCorrector()

def setTimeCorrection(serverUTCTime):
    _g_instance._evalTimeCorrection(serverUTCTime)


def makeLocalServerTime(serverTime):
    if serverTime:
        return serverTime - _g_instance.timeCorrection
    else:
        return None


def makeLocalServerDatetime(serverDatetime):
    if isinstance(serverDatetime, datetime.datetime):
        return serverDatetime - datetime.timedelta(seconds=_g_instance.timeCorrection)
    else:
        return None


def utcToLocalDatetime(utcDatetime):
    return datetime.datetime.fromtimestamp(calendar.timegm(utcDatetime.timetuple()))


def getServerRegionalTime():
    return _g_instance.serverRegionalTime


def getServerRegionalTimeCurrentDay():
    ts = time.gmtime(_g_instance.serverRegionalTime)
    return ts.tm_hour * ONE_HOUR + ts.tm_min * ONE_MINUTE + ts.tm_sec


def getServerRegionalWeekDay():
    return datetime.datetime.utcfromtimestamp(_g_instance.serverRegionalTime).isoweekday()


def getTimeDeltaFromNow(t):
    if t and datetime.datetime.utcfromtimestamp(t) > datetime.datetime.utcnow():
        delta = datetime.datetime.utcfromtimestamp(t) - datetime.datetime.utcnow()
        return delta.days * ONE_DAY + delta.seconds
    return 0


def getTillTimeString(timeValue, keyNamespace):
    gmtime = time.gmtime(timeValue)
    fmtValues = {'day': str(time.struct_time(gmtime).tm_yday),
     'hour': time.strftime('%H', gmtime),
     'min': time.strftime('%M', gmtime),
     'sec': time.strftime('%S', gmtime)}
    if timeValue > ONE_DAY:
        fmtKey = 'days'
    elif ONE_DAY >= timeValue >= ONE_HOUR:
        fmtKey = 'hours'
    else:
        fmtKey = 'min'
    return i18n.makeString(('%s/%s' % (keyNamespace, fmtKey)), **fmtValues)
