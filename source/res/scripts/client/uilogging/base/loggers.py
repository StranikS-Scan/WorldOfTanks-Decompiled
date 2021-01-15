# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/base/loggers.py
import json
import BigWorld
import BattleReplay
from debug_utils_bootcamp import LOG_STATISTIC
from gui.shared.utils import getPlayerDatabaseID
import constants
from wotdecorators import noexcept
from uilogging.logging_constants import FEATURES, STATUS_REQUESTED
from uilogging.helpers import featuresCache
from uilogging import loggingSettings
__all__ = ('BaseLogger', 'isSPAAttributeExists', 'isUILoggingEnabled')

def isSPAAttributeExists():
    if loggingSettings.testMode:
        return True
    else:
        bootcampSPAFlag = BigWorld.player().spaFlags.getFlag(constants.SPA_ATTRS.LOGGING_ENABLED)
        return bootcampSPAFlag and bootcampSPAFlag is not None


def isTokenAvailable(feature):
    try:
        token = BigWorld.player().tokens.getToken(feature)
        currentTime = BigWorld.time()
    except AttributeError:
        return False

    if not token:
        return False
    expireDate, _ = token
    return expireDate > currentTime


def isUILoggingEnabled(feature):
    if not BigWorld.player():
        return False
    if BattleReplay.isPlaying():
        return False
    if not loggingSettings.hostsDefined:
        return False
    if feature == FEATURES.BOOTCAMP:
        return True
    tokenAvailable = isTokenAvailable(feature)
    if tokenAvailable:
        return True
    status = featuresCache.enabledForFeature(feature)
    return True if status == STATUS_REQUESTED else status


class BaseLogger(object):
    _logKey = None
    _validator = None
    _feature = None

    def __init__(self, *args, **kwargs):
        self._player = None
        self._isNewbie = None
        self._ready = False
        self._enabled = False
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
        if loggingSettings.testMode:
            return self._ready
        return False if not loggingSettings.host or not loggingSettings.apiHost else self._ready and self._enabled

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
        self._player = getPlayerDatabaseID()

    def initLogger(self):
        if self.ready:
            return
        else:
            self._init()
            self._isNewbie = None
            self._ready = True
            self._enabled = isUILoggingEnabled(self._feature)
            return

    def logStatistic(self, **kwargs):
        raise NotImplementedError

    def _sendIntoKafka(self, data):
        BigWorld.fetchURL(url=loggingSettings.host, callback=lambda x: x, headers=loggingSettings.headers, timeout=loggingSettings.requestTimeout, method=loggingSettings.httpMethod, postdata=json.dumps(data))

    def _sendIntoClientLog(self, data):
        LOG_STATISTIC(str(data))

    @noexcept
    def sendLogData(self, data):
        if loggingSettings.testMode:
            self._sendIntoClientLog(data)
        self._sendIntoKafka(data)
