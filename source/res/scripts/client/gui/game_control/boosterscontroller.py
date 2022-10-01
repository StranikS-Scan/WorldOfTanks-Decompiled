# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/BoostersController.py
from typing import TYPE_CHECKING
from operator import itemgetter
import BigWorld
import Event
from constants import Configs
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency
from helpers import time_utils
from helpers.server_settings import serverSettingsChangeListener
from skeletons.gui.game_control import IBoostersController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from tutorial.control.context import GLOBAL_FLAG
if TYPE_CHECKING:
    from typing import Dict
    from helpers.server_settings import ServerSettings
    from gui.lobby_context import LobbyContext
    from gui.shared.items_cache import ItemsCache
    from gui.goodies.goodies_cache import GoodiesCache

class BoostersController(IBoostersController, IGlobalListener):
    itemsCache = dependency.descriptor(IItemsCache)
    goodiesCache = dependency.descriptor(IGoodiesCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(BoostersController, self).__init__()
        self.__eventManager = Event.EventManager()
        self.onBoosterChangeNotify = Event.Event(self.__eventManager)
        self.onReserveTimerTick = Event.Event(self.__eventManager)
        self.onGameModeStatusChange = Event.Event(self.__eventManager)
        self.__gameModeSupported = None
        self.__boosterNotifyTimeCallback = None
        self.__boostersForUpdate = []
        self.__notificatorManager = Notifiable()
        self.__serverSettings = None
        self.__supportedQueueTypes = None
        return

    def isGameModeSupported(self):
        return self.__gameModeSupported or False

    def fini(self):
        self._stop()
        super(BoostersController, self).fini()

    def onPrbEntitySwitched(self):
        self.updateGameModeStatus()

    def updateGameModeStatus(self):
        if self.prbDispatcher:
            prbEntity = self.prbDispatcher.getEntity()
            enabled = prbEntity.getQueueType() in self.__supportedQueueTypes
            if self.__gameModeSupported != enabled:
                self.__gameModeSupported = enabled
                self.toggleHangarHint(enabled)
                self.onGameModeStatusChange()

    def toggleHangarHint(self, enabled):
        getTutorialGlobalStorage().setValue(GLOBAL_FLAG.PERSONAL_RESERVES_AVAILABLE, enabled)

    def onLobbyInited(self, event):
        self.startGlobalListening()
        self.itemsCache.onSyncCompleted += self._update
        self.__notificatorManager.addNotificator(PeriodicNotifier(self.__timeTillNextReserveTick, self.onReserveTimerTick, (time_utils.ONE_MINUTE,)))
        self.__notificatorManager.startNotification()
        if self.__boosterNotifyTimeCallback is None:
            self.__startBoosterTimeNotifyCallback()
        self.updateGameModeStatus()
        return

    def onAccountBecomePlayer(self):
        self.__onServerSettingsChanged(self.lobbyContext.getServerSettings())

    def onAvatarBecomePlayer(self):
        self._stop()

    def onDisconnected(self):
        self._stop()

    def _stop(self):
        self.__clearBoosterTimeNotifyCallback()
        self.__notificatorManager.stopNotification()
        self.__notificatorManager.clearNotification()
        self.__boostersForUpdate = None
        self.__eventManager.clear()
        self.itemsCache.onSyncCompleted -= self._update
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onServerSettingsUpdate
        self.stopGlobalListening()
        return

    def _update(self, *args):
        self.__clearBoosterTimeNotifyCallback()
        self.__notificatorManager.startNotification()
        self.__startBoosterTimeNotifyCallback()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onServerSettingsUpdate
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__onServerSettingsUpdate
        self.__updateSettings()
        return

    @serverSettingsChangeListener(Configs.PERSONAL_RESERVES_CONFIG.value)
    def __onServerSettingsUpdate(self, _):
        self.__updateSettings()

    def __updateSettings(self):
        self.__supportedQueueTypes = self.__serverSettings.personalReservesConfig.supportedQueueTypes
        self.updateGameModeStatus()

    def __startBoosterTimeNotifyCallback(self):
        self.__boostersForUpdate = []
        activeBoosters = self.goodiesCache.getBoosters(REQ_CRITERIA.BOOSTER.ACTIVE).values()
        notificationList = []
        for booster in activeBoosters:
            notificationList.append((booster.boosterID, booster.getUsageLeftTime() % time_utils.ONE_MINUTE))

        if notificationList:
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

    def __timeTillNextReserveTick(self):
        clanReserves = self.goodiesCache.getClanReserves().values()
        return min((reserve.getUsageLeftTime() for reserve in clanReserves)) + 1 if clanReserves else 0
