# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/seniority_awards_controller.py
from enum import Enum
import re
from typing import Dict, Iterable, Optional, TYPE_CHECKING
import BigWorld
import Event
import logging
from BWUtil import AsyncReturn
from constants import Configs
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency, time_utils
from skeletons.gui.game_control import ISeniorityAwardsController, IHangarLoadingController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from helpers.server_settings import SeniorityAwardsConfig
from wg_async import wg_async, wg_await, TimeoutError, AsyncEvent, AsyncScope, BrokenPromiseError
if TYPE_CHECKING:
    from gui.server_events.event_items import Quest
REG_EXP_QUEST_YEAR_TIER = ':([Y, y]\\d+):'
REG_EXP_QUEST_TEST_GROUP = ':([A,a,B,b][T,t])'
WDR_CURRENCY = 'wdrcoin'
CLAIM_REWARD_TIMEOUT = 20
SELECT_REWARD_TIMEOUT = 20
NEWBIE_REWARD_BATTLES_COUNT = 15
NEWBIE_BULLET_BATTLES_COUNT = 4
SENIORITY_AWARDS_PREFIX = 'wdr24:'

class VehicleSelectionState(Enum):
    RECIEVED = 0
    SELECTION_FAILED = 1
    HAS_CLIENT_TOKENS = 2


class VehiclesForSelectionState(Enum):
    STATE_CHANGED = 0
    VEHICLES_CHANGED = 1


_logger = logging.getLogger(__name__)

class SeniorityAwardsController(ISeniorityAwardsController):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __eventsCache = dependency.descriptor(IEventsCache)
    __hangarLoadingController = dependency.descriptor(IHangarLoadingController)

    def __init__(self):
        super(SeniorityAwardsController, self).__init__()
        self.__em = Event.EventManager()
        self.onUpdated = Event.Event(self.__em)
        self.onVehicleSelectionChanged = Event.Event(self.__em)
        self.__claimTimeoutId = None
        self.__scope = AsyncScope()
        self.__vehicleSelectionQuestCompletedEvent = AsyncEvent(scope=self.__scope)
        self.__vehicleSelectionQuestId = ''
        self.__years = -1
        self.__yearTier = None
        self.__rewardCategory = None
        self.__testGroup = None
        self.__seniorityAwardsCompletedQuests = None
        self.__vehiclesForSelection = {}
        return

    @property
    def config(self):
        return self.__lobbyContext.getServerSettings().getSeniorityAwardsConfig() if self.__lobbyContext else SeniorityAwardsConfig()

    @property
    def isEnabled(self):
        return self.config.enabled

    @property
    def isActive(self):
        return self.config.active

    @property
    def isAvailable(self):
        return self.isEnabled and self.isActive

    @property
    def timeLeft(self):
        return self.config.endTime - time_utils.getServerUTCTime() if self.isEnabled else -1

    @property
    def endTime(self):
        return self.config.endTime

    @property
    def isVehicleSelectionAvailable(self):
        return bool(self.isAvailable and not self.__hasClientTokens() and self.__itemsCache.items.tokens.isTokenAvailable(self.vehicleSelectionToken) and self.vehiclesForSelection)

    @property
    def yearsInGame(self):
        if self.__years < 0 and self.yearTier:
            self.__years = int(self.yearTier[1:])
        return self.__years

    @property
    def getVehiclesForSelectionCount(self):

        def __vehicleSelectionFilterFunc(q):
            return q.getID().startswith(self.vehicleSelectionQuestPrefix)

        vehCanSelectAmm = 0
        for quest in self.__eventsCache.getHiddenQuests(__vehicleSelectionFilterFunc).values():
            vehicleBonuses = quest.getBonuses('vehicles')
            if vehicleBonuses:
                questsBonusVehAmm = len(vehicleBonuses[0].getValue())
                vehCanSelectAmm = max(vehCanSelectAmm, questsBonusVehAmm)

        return vehCanSelectAmm

    @property
    def isRewardReceived(self):
        return self.__itemsCache.items.tokens.isTokenAvailable(self.config.receivedRewardsToken)

    @property
    def seniorityQuestPrefix(self):
        return self.config.rewardQuestsPrefix

    @property
    def vehicleSelectionQuestPattern(self):
        return self.config.vehicleSelectionQuestPattern.format(category=self.rewardCategory or self.testGroup)

    @property
    def vehicleSelectionQuestPrefix(self):
        return self.vehicleSelectionQuestPattern.format(id='')

    @property
    def vehicleSelectionToken(self):
        return self.config.vehicleSelectionTokenPattern.format(category=self.rewardCategory or self.testGroup)

    @property
    def categories(self):
        return self.config.categories

    @property
    def showRewardHangarNotification(self):
        return False

    @property
    def showRewardNotification(self):
        return self.config.showRewardNotification

    @property
    def isEligibleToReward(self):
        return self.isEnabled and self.__itemsCache.items.tokens.isTokenAvailable(self.config.rewardEligibilityToken)

    @property
    def isNeedToShowRewardNotification(self):
        battlesCount = self.__itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount()
        orConditions = self.showRewardNotification or battlesCount < NEWBIE_REWARD_BATTLES_COUNT
        return self.isAvailable and self.__hangarSpace.spaceInited and self.isEligibleToReward and not self.isRewardReceived and orConditions

    @property
    def isNeedToShowNotificationBullet(self):
        battlesCount = self.__itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount()
        return battlesCount > NEWBIE_BULLET_BATTLES_COUNT

    @property
    def clockOnNotification(self):
        return self.config.clockOnNotification

    def getSACoin(self):
        return self.__itemsCache.items.stats.dynamicCurrencies.get(WDR_CURRENCY, 0)

    @property
    def claimVehicleRewardTokenPattern(self):
        return self.config.claimVehicleRewardTokenPattern.format(category=self.rewardCategory or self.testGroup)

    @property
    def pendingReminderTimestamp(self):
        if not self.isAvailable:
            return None
        else:
            timestamp = time_utils.getServerUTCTime()
            reminders = self.config.reminders
            pendingNotifications = [ reminderTS for reminderTS in reminders if reminderTS < timestamp ]
            return max(pendingNotifications) if pendingNotifications else None

    @property
    def completedSeniorityAwardsQuests(self):
        if self.__seniorityAwardsCompletedQuests is None:

            def __questCompletedFilterFunc(q):
                return self.__filterFunc(q) and q.isCompleted()

            self.__seniorityAwardsCompletedQuests = self.__eventsCache.getHiddenQuests(__questCompletedFilterFunc)
        return self.__seniorityAwardsCompletedQuests

    @property
    def vehiclesForSelection(self):
        if not self.__vehiclesForSelection:
            self.__vehiclesForSelection = self.getAvailableVehicleSelectionRewards()
        return self.__vehiclesForSelection

    @property
    def rewardCategory(self):
        if self.__rewardCategory is None:
            self.__rewardCategory = ''
            for idx, years in self.categories.items():
                if self.yearsInGame in years:
                    self.__rewardCategory = idx
                    break

        return self.__rewardCategory

    @property
    def testGroup(self):
        if self.__testGroup is None:
            self.__testGroup = self.getSeniorityLevel(self.completedSeniorityAwardsQuests.keys(), REG_EXP_QUEST_TEST_GROUP)
        return self.__testGroup

    @property
    def yearTier(self):
        if self.__yearTier is None:
            self.__yearTier = self.getSeniorityLevel(self.completedSeniorityAwardsQuests.keys(), REG_EXP_QUEST_YEAR_TIER)
        return self.__yearTier

    def isVehicleSelectionQuestCompleted(self, vehicleRewardId):
        return self.vehicleSelectionQuestPattern.format(id=vehicleRewardId) in self.completedSeniorityAwardsQuests

    def getVehicleSelectionRewards(self):

        def __vehicleSelectionFilterFunc(q):
            qId = q.getID()
            return qId.startswith(pattern)

        pattern = self.vehicleSelectionQuestPrefix
        bonusVehicles = {}
        for quest in self.__eventsCache.getHiddenQuests(__vehicleSelectionFilterFunc).values():
            rewardId = quest.getID().split(':')[-1]
            for vehBonus in quest.getBonuses('vehicles'):
                vehicles = vehBonus.getValue()
                for intCD in vehicles.iterkeys():
                    bonusVehicles[rewardId] = self.__itemsCache.items.getItemByCD(intCD)

        return bonusVehicles

    def getAvailableVehicleSelectionRewards(self):
        return {key:value for key, value in self.getVehicleSelectionRewards().items() if self.__itemsCache.items.inventory.getItemData(value.intCD) is None}

    @wg_async
    def selectVehicleReward(self, vehicleRewardId):
        if self.isVehicleSelectionAvailable:
            self.__vehicleSelectionQuestId = vehicleRewardId
            token = self.claimVehicleRewardTokenPattern.format(id=vehicleRewardId)
            BigWorld.player().requestSingleToken(token)
            try:
                try:
                    yield wg_await(self.__vehicleSelectionQuestCompletedEvent.wait(), timeout=SELECT_REWARD_TIMEOUT)
                    result = VehicleSelectionState.RECIEVED
                except TimeoutError:
                    result = VehicleSelectionState.SELECTION_FAILED
                except BrokenPromiseError:
                    _logger.debug('%s has been destroyed before %s completed', self, self.vehicleSelectionQuestPattern.format(id=self.__vehicleSelectionQuestId))
                    result = VehicleSelectionState.SELECTION_FAILED

            finally:
                self.__vehicleSelectionQuestId = ''

        else:
            result = VehicleSelectionState.HAS_CLIENT_TOKENS
        raise AsyncReturn(result)

    def getVehicleSelectionQuestReward(self, vehicleRewardId):
        return self.getVehicleSelectionRewards()[vehicleRewardId] if self.isVehicleSelectionQuestCompleted(vehicleRewardId) else None

    def claimReward(self):
        self.__showWaiting()
        self.__scheduleClaimTimeout()
        BigWorld.player().requestSingleToken(self.config.claimRewardToken)

    def markRewardReceived(self):
        self.__hideWaiting()
        self.__cancelClaimTimeout()

    @staticmethod
    def getSeniorityLevel(completedQuests, regexp):
        seniorityLvl = ''
        if regexp:
            for questID in completedQuests:
                seniorityLvlSearch = re.search(regexp, questID)
                if seniorityLvlSearch is not None:
                    seniorityLvl = seniorityLvl or seniorityLvlSearch.groups(default='')[0]

        return seniorityLvl

    def onLobbyInited(self, event):
        super(SeniorityAwardsController, self).onLobbyInited(event)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChanged
        self.__itemsCache.onSyncCompleted += self.__onItemsCacheUpdated
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__eventsCache.onSyncCompleted += self.__onEventsCacheSynced
        if self.__hangarSpace.spaceInited:
            self.__update()
        else:
            self.__hangarSpace.onSpaceCreate += self.__onHangarLoaded

    def onAccountBecomeNonPlayer(self):
        super(SeniorityAwardsController, self).onAccountBecomeNonPlayer()
        self.__clear()

    def fini(self):
        self.__em.clear()
        self.__clear()
        self.__scope.destroy()
        super(SeniorityAwardsController, self).fini()

    def onDisconnected(self):
        self.__clear()
        super(SeniorityAwardsController, self).onDisconnected()

    def onAvatarBecomePlayer(self):
        self.__removeListeners()
        super(SeniorityAwardsController, self).onAvatarBecomePlayer()

    def __onHangarLoaded(self):
        self.__update()

    def __clear(self):
        self.__removeListeners()
        self.__cancelClaimTimeout()
        self.__vehicleSelectionQuestId = ''
        self.__endTimestamp = None
        self.__clockOnNotification = None
        self.__vehicleSelectionQuestCompletedEvent.clear()
        self.__clearCachedValues()
        return

    def __clearCachedValues(self):
        self.__rewardCategory = None
        self.__testGroup = None
        self.__seniorityAwardsCompletedQuests = None
        self.__vehiclesForSelection.clear()
        self.__years = -1
        self.__yearTier = None
        return

    def __removeListeners(self):
        self.__eventsCache.onSyncCompleted -= self.__onEventsCacheSynced
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChanged
        self.__itemsCache.onSyncCompleted -= self.__onItemsCacheUpdated
        self.__hangarSpace.onSpaceCreate -= self.__onHangarLoaded
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onTokensUpdate(self, diff):
        eligibilityToken = self.config.rewardEligibilityToken
        if eligibilityToken and eligibilityToken in diff:
            self.__update()
        return self.__onVehicleSelectionStateChanged() if self.vehicleSelectionToken in diff else None

    def __onSettingsChanged(self, diff):
        if Configs.SENIORITY_AWARDS_CONFIG.value in diff:
            self.__update()

    def __scheduleClaimTimeout(self):
        self.__cancelClaimTimeout()
        self.__claimTimeoutId = BigWorld.callback(CLAIM_REWARD_TIMEOUT, self.__onClaimRewardFailed)

    def __cancelClaimTimeout(self):
        if self.__claimTimeoutId:
            BigWorld.cancelCallback(self.__claimTimeoutId)
            self.__claimTimeoutId = None
        return

    def __onClaimRewardFailed(self):
        self.__cancelClaimTimeout()
        self.__hideWaiting()
        SystemMessages.pushI18nMessage('#system_messages:seniority_awards/claim_reward_failed', type=SystemMessages.SM_TYPE.Error, priority=NotificationPriorityLevel.HIGH)

    @staticmethod
    def __showWaiting():
        Waiting.show('claimSeniorityAwards')

    @staticmethod
    def __hideWaiting():
        Waiting.hide('claimSeniorityAwards')

    def __update(self):
        self.onUpdated()

    @staticmethod
    def __filterFunc(quest):
        qId = quest.getID()
        return qId.startswith(SENIORITY_AWARDS_PREFIX)

    def __onEventsCacheSynced(self, *_, **__):
        self.__clearCachedValues()
        if self.__vehicleSelectionQuestId and not self.__vehicleSelectionQuestCompletedEvent.is_set() and self.isVehicleSelectionQuestCompleted(self.__vehicleSelectionQuestId):
            self.__vehicleSelectionQuestCompletedEvent.set()

    def __hasClientTokens(self):
        pattern = self.claimVehicleRewardTokenPattern.format(id='')
        return bool([ token for token in self.__itemsCache.items.tokens.getTokens() if token.startswith(pattern) ])

    def __onItemsCacheUpdated(self, reason, diff):
        if reason != CACHE_SYNC_REASON.CLIENT_UPDATE or diff is None or GUI_ITEM_TYPE.VEHICLE not in diff:
            return
        elif not self.isVehicleSelectionAvailable:
            return
        else:
            vehDiff = diff[GUI_ITEM_TYPE.VEHICLE]
            receivedVehicles = [ key for key, vehicle in self.vehiclesForSelection.items() if vehicle.intCD in vehDiff ]
            if receivedVehicles:
                for key in receivedVehicles:
                    self.vehiclesForSelection.pop(key, None)

                self.onVehicleSelectionChanged(VehiclesForSelectionState.VEHICLES_CHANGED)
            if not self.vehiclesForSelection:
                self.__onVehicleSelectionStateChanged()
            return

    def __onVehicleSelectionStateChanged(self):
        self.onVehicleSelectionChanged(VehiclesForSelectionState.STATE_CHANGED)
