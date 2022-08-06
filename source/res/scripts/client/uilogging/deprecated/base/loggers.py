# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/deprecated/base/loggers.py
import BigWorld
from helpers import dependency
from skeletons.ui_logging import IUILoggingCore
from uilogging.base.logger import _BaseLogger
from uilogging.constants import LogLevels
from wotdecorators import noexcept
__all__ = ('BaseLogger', 'isUILoggingEnabled', 'CommonLogger')

def isUILoggingEnabled(feature):
    uiLoggingCore = dependency.instance(IUILoggingCore)
    return uiLoggingCore.isFeatureEnabled(feature)


class BaseLogger(object):
    _logKey = None
    _validator = None
    _feature = None

    def __init__(self, *args, **kwargs):
        self._isNewbie = None
        self._ready = False
        self._avatar = None
        self._populateTime = None
        return

    def _resetTime(self, resetTime):
        if resetTime:
            self._populateTime = int(BigWorld.time())

    @classmethod
    def setLogKey(cls, logKey):
        cls._logKey = logKey

    @property
    def ready(self):
        return self._ready and isUILoggingEnabled(self._feature)

    @property
    def feature(self):
        return self._feature

    @property
    def arena(self):
        if self._avatar:
            try:
                return self._avatar.arena
            except AttributeError:
                return None

        return None

    @property
    def peripheryID(self):
        if self._avatar:
            try:
                return self._avatar.connectionMgr.peripheryID
            except AttributeError:
                return None

        return None

    @property
    def arenaID(self):
        arenaUniqueID = None
        if self.arena:
            arenaUniqueID = self.arena.arenaUniqueID
        return arenaUniqueID

    def _init(self):
        self._avatar = BigWorld.player()

    def initLogger(self):
        if self._ready:
            return
        else:
            self._init()
            self._isNewbie = None
            self._ready = True
            return

    def logStatistic(self, **kwargs):
        raise NotImplementedError

    @noexcept
    def sendLogData(self, action, **params):
        uiLoggingCore = dependency.instance(IUILoggingCore)
        return uiLoggingCore.log(self._feature, self._logKey, action, **params)


class CommonLogger(_BaseLogger):
    __slots__ = ()

    def log(self, action, loglevel=LogLevels.INFO, **params):
        self._log(action, loglevel, **params)

    def logOnce(self, action, loglevel=LogLevels.INFO, **params):
        self._logOnce(action, loglevel, **params)

    def stopAction(self, action, loglevel=LogLevels.INFO, timeLimit=0, **params):
        self._stopAction(action, loglevel, timeLimit, **params)
