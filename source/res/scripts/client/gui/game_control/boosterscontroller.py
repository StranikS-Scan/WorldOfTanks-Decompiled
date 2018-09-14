# Embedded file name: scripts/client/gui/game_control/BoostersController.py
from operator import itemgetter
import BigWorld
import Event
from gui.game_control.controllers import Controller
from gui.goodies.GoodiesCache import g_goodiesCache
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import time_utils

class BoostersController(Controller):

    def __init__(self, proxy):
        super(BoostersController, self).__init__(proxy)
        self.onBoosterChangeNotify = Event.Event()
        self.__boosterNotifyTimeCallback = None
        self.__boostersForUpdate = []
        return

    def fini(self):
        self._stop()
        super(BoostersController, self).fini()

    def onLobbyInited(self, event):
        g_itemsCache.onSyncCompleted += self._update
        if self.__boosterNotifyTimeCallback is None:
            self.__startBoosterTimeNotifyCallback()
        return

    def onAvatarBecomePlayer(self):
        self._stop()

    def onDisconnected(self):
        self._stop()

    def _stop(self):
        self.__clearBoosterTimeNotifyCallback()
        self.__boostersForUpdate = None
        self.onBoosterChangeNotify.clear()
        g_itemsCache.onSyncCompleted -= self._update
        return

    def _update(self, *args):
        self.__clearBoosterTimeNotifyCallback()
        self.__startBoosterTimeNotifyCallback()

    def __startBoosterTimeNotifyCallback(self):
        self.__boostersForUpdate = []
        activeBoosters = g_goodiesCache.getBoosters(REQ_CRITERIA.BOOSTER.ACTIVE).values()
        notificationList = []
        for booster in activeBoosters:
            notificationList.append((booster.boosterID, booster.getUsageLeftTime() % time_utils.ONE_MINUTE))

        if len(notificationList) > 0:
            _, nextBoosterNotification = min(notificationList, key=itemgetter(1))
            for item in notificationList:
                if item[1] == nextBoosterNotification:
                    self.__boostersForUpdate.append(item[0])

            nextBoosterNotification = max(nextBoosterNotification, 1)
        else:
            return
        self.__boosterNotifyTimeCallback = BigWorld.callback(nextBoosterNotification, self.__notifyBoosterTime)

    def __notifyBoosterTime(self):
        self.__boosterNotifyTimeCallback = None
        self.onBoosterChangeNotify(self.__boostersForUpdate)
        self.__startBoosterTimeNotifyCallback()
        return

    def __clearBoosterTimeNotifyCallback(self):
        if self.__boosterNotifyTimeCallback is not None:
            BigWorld.cancelCallback(self.__boosterNotifyTimeCallback)
            self.__boosterNotifyTimeCallback = None
        return
