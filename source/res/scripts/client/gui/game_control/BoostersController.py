# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/BoostersController.py
import logging
from typing import TYPE_CHECKING
import Event
from adisp import adisp_process
from constants import Configs, QUEUE_TYPE
from goodies.goodie_constants import BoosterCategory
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.prb_getters import getQueueTypeFromEntityType, isDevTraining
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.server_events import settings
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency, time_utils
from helpers.server_settings import serverSettingsChangeListener
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from skeletons.gui.game_control import IBoostersController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
if TYPE_CHECKING:
    from typing import Dict, TypeVar
    from helpers.server_settings import ServerSettings
    from gui.lobby_context import LobbyContext
    from gui.shared.items_cache import ItemsCache
    from gui.goodies.goodies_cache import GoodiesCache
    from gui.prb_control.entities.base.entity import BasePrbEntity
    from gui.prb_control.entities.base.legacy.entity import LegacyEntity
    from gui.server_events.settings import _PersonalReservesSettings
    PrbEntityType = TypeVar('PrbEntityType', bound=BasePrbEntity)
    LegacyEntityType = TypeVar('LegacyEntityType', bound=LegacyEntity)
_logger = logging.getLogger(__name__)

class BoostersController(IBoostersController, IGlobalListener):
    itemsCache = dependency.descriptor(IItemsCache)
    goodiesCache = dependency.descriptor(IGoodiesCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self):
        super(BoostersController, self).__init__()
        self.__eventManager = Event.EventManager()
        self.onPersonalReserveTick = Event.Event(self.__eventManager)
        self.onClanReserveTick = Event.Event(self.__eventManager)
        self.onBoostersDataUpdate = Event.Event(self.__eventManager)
        self.onGameModeStatusChange = Event.Event(self.__eventManager)
        self.__enabledCategories = set()
        self.__boostersForUpdate = []
        self.__notificatorManager = Notifiable()
        self.__serverSettings = None
        self.__supportedQueueTypes = {}
        self.soonExpireNotificationDisplayed = False
        return

    def isGameModeSupported(self, category=None):
        return bool(self.__enabledCategories) if category is None else category in self.__enabledCategories

    def fini(self):
        self._stop()
        super(BoostersController, self).fini()

    def onPrbEntitySwitched(self):
        self.updateGameModeStatus()

    def updateGameModeStatus(self):
        if self.prbDispatcher is not None:
            enabledCategories = set()
            queueType = self.__getQueueType(self.prbDispatcher.getEntity())
            isDevTrainingBattle = isDevTraining()
            for category in BoosterCategory:
                if queueType in self.__supportedQueueTypes[category.name] or isDevTrainingBattle:
                    enabledCategories.add(category)

            isChanged = enabledCategories != self.__enabledCategories
            self.__enabledCategories = enabledCategories
            if isChanged:
                self.onGameModeStatusChange()
        return

    def shouldShowOnBoardingCardHint(self, boosterID):
        return boosterID not in settings.getPersonalReservesSettings().boosterCardHintsSeen

    def setCardHintSeenFor(self, boosterID):
        with settings.personalReservesSettings() as prSettings:
            prSettings.addBoosterToCardHintsSeen(boosterID)

    @adisp_process
    def selectRandomBattle(self):
        dispatcher = self.prbDispatcher
        if dispatcher is not None:
            result = yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
            if not result:
                _logger.error('Could not switch to random battle.')
        else:
            _logger.error('Prebattle dispatcher is not defined.')
        return

    def getExpirableBoosters(self):
        criteria = REQ_CRITERIA.BOOSTER.IN_ACCOUNT | REQ_CRITERIA.BOOSTER.ENABLED | REQ_CRITERIA.BOOSTER.LIMITED
        return self.goodiesCache.getBoosters(criteria=criteria)

    def onLobbyInited(self, event):
        self.startGlobalListening()
        self.itemsCache.onSyncCompleted += self._update
        self.__notificatorManager.addNotificators(PeriodicNotifier(self.__timeTillNextClanReserveTick, self.onClanReserveTick, (time_utils.ONE_MINUTE,)), PeriodicNotifier(self.__timeTillNextPersonalReserveTick, self.__notifyBoosterTime, (time_utils.ONE_MINUTE,)))
        self.__notificatorManager.startNotification()
        g_clientUpdateManager.addCallbacks({'cache.activeOrders': self._update,
         'goodies': self._update})
        self.updateGameModeStatus()

    def onAccountBecomePlayer(self):
        self.__onServerSettingsChanged(self.lobbyContext.getServerSettings())

    def onAvatarBecomePlayer(self):
        self._stop()

    def onDisconnected(self):
        self.soonExpireNotificationDisplayed = False
        self._stop()

    def _stop(self):
        self.__notificatorManager.stopNotification()
        self.__notificatorManager.clearNotification()
        self.__boostersForUpdate = None
        self.__eventManager.clear()
        self.itemsCache.onSyncCompleted -= self._update
        g_clientUpdateManager.removeObjectCallbacks(self)
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onServerSettingsUpdate
        self.stopGlobalListening()
        return

    def _update(self, *args):
        self.__notificatorManager.startNotification()
        self.__processNotifications()
        self.onBoostersDataUpdate()

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

    def __timeTillNextPersonalReserveTick(self):
        activeBoosters = self.goodiesCache.getBoosters(REQ_CRITERIA.BOOSTER.ACTIVE).values()
        return min((booster.getUsageLeftTime() for booster in activeBoosters)) if activeBoosters else 0

    def __notifyBoosterTime(self):
        self.onPersonalReserveTick()

    def __timeTillNextClanReserveTick(self):
        clanReserves = self.goodiesCache.getClanReserves().values()
        return min((reserve.getUsageLeftTime() for reserve in clanReserves)) + 1 if clanReserves else 0

    def __getQueueType(self, prbEntity):
        return prbEntity.getQueueType() if prbEntity.getQueueType() > QUEUE_TYPE.UNKNOWN else getQueueTypeFromEntityType(prbEntity.getEntityType())

    def __processNotifications(self):
        with settings.personalReservesSettings() as prSettings:
            self.__processFirstExpirationsNotification(prSettings)
        self.__processSoonExpirationsNotification()

    def __processFirstExpirationsNotification(self, accountSettings):
        if accountSettings.isFirstTimeNotificationShown:
            return
        totalBoostersCount = 0
        for booster in self.getExpirableBoosters().itervalues():
            totalBoostersCount += booster.count

        if totalBoostersCount > 0:
            self.systemMessages.proto.serviceChannel.pushClientMessage({'values': str(totalBoostersCount)}, SCH_CLIENT_MSG_TYPE.PERSONAL_RESERVES_FIRST_LOGIN)
            accountSettings.setIsFirstTimeNotificationShown(True)

    def __processSoonExpirationsNotification(self):
        if self.soonExpireNotificationDisplayed:
            return
        totalBoostersCount = 0
        for booster in self.getExpirableBoosters().itervalues():
            expirations = booster.expirations
            for variant in expirations.itervalues():
                expireInTime = time_utils.getTimeDeltaFromNow(variant.timestamp)
                if expireInTime < time_utils.ONE_DAY:
                    totalBoostersCount += variant.amount

        if totalBoostersCount > 0:
            self.systemMessages.proto.serviceChannel.pushClientMessage({'values': str(totalBoostersCount)}, SCH_CLIENT_MSG_TYPE.PERSONAL_RESERVES_SOON_EXPIRATION)
            self.soonExpireNotificationDisplayed = True
