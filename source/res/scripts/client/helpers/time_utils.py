# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/time_utils.py
# Compiled at: 2011-06-21 13:32:19
import time, BigWorld
import datetime
import calendar

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
