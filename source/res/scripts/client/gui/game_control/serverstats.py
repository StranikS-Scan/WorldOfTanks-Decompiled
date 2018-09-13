# Embedded file name: scripts/client/gui/game_control/ServerStats.py
import BigWorld
import constants
import Event
from PlayerEvents import g_playerEvents
from debug_utils import LOG_DEBUG

class ServerStats(object):
    STATS_REQUEST_TIMEOUT = 5.0
    onStatsReceived = Event.Event()

    def init(self):
        self.__statsCallbackID = None
        self.__stats = {}
        return

    def fini(self):
        pass

    def start(self):
        g_playerEvents.onServerStatsReceived += self.__onStatsReceived
        self.__loadStatsCallback(0.0)

    def stop(self):
        g_playerEvents.onServerStatsReceived -= self.__onStatsReceived
        self.__clearStatsCallback()

    def getStats(self):
        return self.__stats

    def __onStatsReceived(self, stats):
        self.__stats = stats
        self.onStatsReceived(stats)
        self.__loadStatsCallback()

    def __requestServerStats(self):
        self.__clearStatsCallback()
        if hasattr(BigWorld.player(), 'requestServerStats'):
            BigWorld.player().requestServerStats()

    def __loadStatsCallback(self, timeout = None):
        if constants.IS_SHOW_SERVER_STATS:
            self.__statsCallbackID = BigWorld.callback(timeout if timeout is not None else self.STATS_REQUEST_TIMEOUT, self.__requestServerStats)
        return

    def __clearStatsCallback(self):
        if self.__statsCallbackID is not None:
            BigWorld.cancelCallback(self.__statsCallbackID)
            self.__statsCallbackID = None
        return
