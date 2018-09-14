# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/ServerStats.py
import BigWorld
import Event
import constants
from PlayerEvents import g_playerEvents
from gui.Scaleform.locale.MENU import MENU
from gui.shared.formatters import text_styles
from skeletons.gui.game_control import IServerStatsController
_STATS_REQUEST_TIMEOUT = 5.0

class STATS_TYPE(object):
    UNAVAILABLE = 'unavailable'
    CLUSTER = 'clusterCCU'
    FULL = 'regionCCU/clusterCCU'


class ServerStats(IServerStatsController):

    def __init__(self):
        super(ServerStats, self).__init__()
        self.__statsCallbackID = None
        self.__stats = {}
        self.onStatsReceived = Event.Event()
        return

    def onLobbyStarted(self, ctx):
        g_playerEvents.onServerStatsReceived += self.__onStatsReceived
        self.__loadStatsCallback(0.0)

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__stop()

    def getFormattedStats(self):
        """ Get stats formatted as a single string with applied style.
        """
        clusterUsers, regionUsers, tooltipType = self.getStats()
        if tooltipType == STATS_TYPE.CLUSTER:
            statsStr = clusterUsers
        elif tooltipType == STATS_TYPE.UNAVAILABLE:
            statsStr = text_styles.main(MENU.ONLINECOUNTER_UNAVAILABLE)
        else:
            statsStr = text_styles.concatStylesToSingleLine(text_styles.stats(clusterUsers), text_styles.main(MENU.ONLINECOUNTER_DELIMITER), text_styles.main(regionUsers))
        return (statsStr, tooltipType)

    def getStats(self):
        """ Get stats separately for cluster and region without style.
        """
        clusterCCU = self.__stats.get('clusterCCU', 0)
        regionCCU = self.__stats.get('regionCCU', 0)
        if regionCCU:
            clusterUsers = BigWorld.wg_getIntegralFormat(clusterCCU)
            regionUsers = BigWorld.wg_getIntegralFormat(regionCCU)
            if clusterCCU == regionCCU:
                tooltipType = STATS_TYPE.CLUSTER
            else:
                tooltipType = STATS_TYPE.FULL
        else:
            clusterUsers = regionUsers = '-'
            tooltipType = STATS_TYPE.UNAVAILABLE
        return (clusterUsers, regionUsers, tooltipType)

    def __stop(self):
        g_playerEvents.onServerStatsReceived -= self.__onStatsReceived
        self.__clearStatsCallback()

    def __onStatsReceived(self, stats):
        self.__stats = dict(stats)
        self.onStatsReceived()
        self.__loadStatsCallback()

    def __requestServerStats(self):
        self.__clearStatsCallback()
        if hasattr(BigWorld.player(), 'requestServerStats'):
            BigWorld.player().requestServerStats()

    def __loadStatsCallback(self, timeout=None):
        if constants.IS_SHOW_SERVER_STATS:
            self.__statsCallbackID = BigWorld.callback(timeout if timeout is not None else _STATS_REQUEST_TIMEOUT, self.__requestServerStats)
        return

    def __clearStatsCallback(self):
        if self.__statsCallbackID is not None:
            BigWorld.cancelCallback(self.__statsCallbackID)
            self.__statsCallbackID = None
        return
