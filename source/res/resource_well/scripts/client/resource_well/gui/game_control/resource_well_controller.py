# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/game_control/resource_well_controller.py
import logging
import typing
from Event import Event, EventManager
from PlayerEvents import g_playerEvents
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils
from helpers.events_handler import EventsHandler
from helpers.server_settings import serverSettingsChangeListener
from resource_well.gui.feature.constants import PurchaseMode, DEFAULT_SEASON_NUMBER
from resource_well.gui.feature.number_requester import ResourceWellNumberRequester
from resource_well.gui.feature.resource_well_helpers import getForbiddenAccountToken
from resource_well.gui.feature.resource_well_sync_data import ResourceWellSyncData
from resource_well.helpers.server_settings import ResourceWellConfig
from resource_well_common.feature_constants import RESOURCE_WELL_GAME_PARAMS_KEY, RESOURCE_WELL_PDATA_KEY
from shared_utils import first, makeTupleByDict
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.resource_well import IResourceWellController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, Optional, Set, List, Any
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)

class ResourceWellController(IResourceWellController, EventsHandler):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__eventsManager = EventManager()
        self.onEventUpdated = Event(self.__eventsManager)
        self.onSettingsChanged = Event(self.__eventsManager)
        self.onNumberRequesterUpdated = Event(self.__eventsManager)
        self.__notifier = None
        self.__numberRequesters = {}
        self.__syncData = ResourceWellSyncData()
        self.__config = None
        self.__currentPurchaseMode = None
        return

    @property
    def config(self):
        if self.__config is None:
            self.__config = self.__createConfig()
        return self.__config

    def onLobbyInited(self, event):
        self.__initNumberRequesters()
        self.__setNumberInitialValues()
        self._subscribe()
        if self.__notifier is None:
            self.__notifier = SimpleNotifier(self.__getTimeLeft, self.__onEventStateChange)
        self.__notifier.startNotification()
        return

    def onAvatarBecomePlayer(self):
        self.__config = None
        self.__stop()
        return

    def onDisconnected(self):
        self.__stop()
        self.__clear()

    def init(self):
        g_playerEvents.onClientUpdated += self.__onClientUpdated

    def fini(self):
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        self.__eventsManager.clear()
        self.__stop()
        self.__clear()

    def isEnabled(self):
        return self.config.isEnabled

    def isActive(self):
        return self.isEnabled() and self.isStarted() and not self.isFinished()

    def isStarted(self):
        return self.config.startTime <= time_utils.getServerUTCTime()

    def isFinished(self):
        return self.config.finishTime <= time_utils.getServerUTCTime()

    def isNotStarted(self):
        return self.isEnabled() and not self.isStarted()

    def isPaused(self):
        return not self.isEnabled() and self.isStarted() and not self.isFinished()

    def isForbiddenAccount(self):
        return self.__itemsCache.items.tokens.getToken(getForbiddenAccountToken(resourceWell=self)) is not None

    def isSeasonNumberDefault(self):
        return self.__syncData.getSeason() == DEFAULT_SEASON_NUMBER

    def getRewardLimit(self, rewardID):
        rewardConfig = self.config.getRewardConfig(rewardID)
        return rewardConfig.limit

    def getCurrentPoints(self):
        return self.__syncData.getCurrentPoints()

    def getCurrentRewardID(self):
        return self.__syncData.getCurrentRewardID()

    def getReceivedRewardIDs(self):
        return self.__syncData.getReward()

    def isRewardReceived(self, rewardID):
        return rewardID in self.getReceivedRewardIDs()

    def getBalance(self):
        return self.__syncData.getBalance()

    def getPurchaseMode(self):
        if self.__currentPurchaseMode is not None:
            return self.__currentPurchaseMode
        else:
            self.__currentPurchaseMode = PurchaseMode.ONE_SERIAL_PRODUCT
            rewards = self.config.rewards
            if len(rewards) > 1:
                if any([ r.isSerial for r in rewards.values() ]):
                    self.__currentPurchaseMode = PurchaseMode.SEQUENTIAL_PRODUCT
                elif not any([ r.availableAfter for r in rewards.values() ]):
                    self.__currentPurchaseMode = PurchaseMode.TWO_PARALLEL_PRODUCTS
            return self.__currentPurchaseMode

    def getRewardVehicle(self, rewardID):
        rewardConfig = self.config.getRewardConfig(rewardID)
        vehicleCD = first(rewardConfig.bonus.get('vehicles', {}).keys())
        if vehicleCD is None:
            _logger.error('Vehicle is not found in config.')
            return
        else:
            return self.__itemsCache.items.getItemByCD(vehicleCD)

    def getRewardStyleID(self, rewardID):
        rewardConfig = self.config.getRewardConfig(rewardID)
        return None if not rewardConfig.isSerial else first(rewardConfig.bonus['vehicles'].values(), {}).get('customization', {}).get('styleId')

    def getRewardSequence(self, rewardID):
        rewardConfig = self.config.getRewardConfig(rewardID)
        return rewardConfig.sequence

    def getRewardLeftCount(self, rewardID):
        rewardConfig = self.config.getRewardConfig(rewardID)
        return (self.__getSerialRewardLeftCount(rewardID) if rewardConfig.isSerial else self.__getRegularRewardLeftCount(rewardID)) or 0

    def isParentRewardAvailable(self, rewardID):
        rewardConfig = self.config.getRewardConfig(rewardID)
        return False if not rewardConfig.availableAfter else self.isRewardAvailable(rewardConfig.availableAfter)

    def isRewardAvailable(self, rewardID):
        vehicle = self.getRewardVehicle(rewardID)
        if vehicle and vehicle.isInInventory:
            return False
        parentalRewardID = self.config.getParentRewardID(rewardID=rewardID)
        if self.isRewardReceived(rewardID) or self.isRewardReceived(parentalRewardID):
            return False
        rewardLeftCount = self.getRewardLeftCount(rewardID=rewardID)
        if not parentalRewardID:
            return rewardLeftCount > 0
        parentalRewardLeftCount = self.getRewardLeftCount(rewardID=parentalRewardID)
        return parentalRewardLeftCount == 0 and rewardLeftCount > 0

    def isRewardCountAvailable(self, rewardID):
        requester = self.__numberRequesters.get(rewardID)
        if not requester:
            _logger.error('Requester not found. rewardID: %s', rewardID)
            return False
        return requester.isDataAvailable()

    def getAvailableRewards(self):
        return [ rewardID for rewardID in self.config.rewards if self.isRewardAvailable(rewardID) ]

    def isRewardsOver(self):
        return not any(self.getAvailableRewards()) or self.isSeasonNumberDefault()

    def isRewardVehicle(self, vehicleCD):
        if not self.isActive():
            return False
        for rewardID in self.config.rewards:
            vehicle = self.getRewardVehicle(rewardID)
            if vehicle.intCD == vehicleCD:
                return True

        return False

    def startNumberRequesters(self):
        if self.isEnabled():
            self.__setNumberInitialValues()
            for requester in self.__numberRequesters.values():
                requester.start()

    def stopNumberRequesters(self):
        for requester in self.__numberRequesters.values():
            requester.stop()

    def _getEvents(self):
        return ((self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),)

    def _getCallbacks(self):
        return (('tokens', self.__onTokensUpdated), ('inventory.1.compDescr', self.__onInventoryUpdated))

    def __getTimeLeft(self):
        if not self.isStarted():
            return max(0, self.config.startTime - time_utils.getServerUTCTime())
        return max(0, self.config.finishTime - time_utils.getServerUTCTime()) if not self.isFinished() else 0

    def __onEventStateChange(self):
        self.onEventUpdated()

    def __onInventoryUpdated(self, _):
        if self.isActive():
            self.onEventUpdated()

    def __getRegularRewardLeftCount(self, rewardID):
        requester = self.__numberRequesters.get(rewardID)
        if not requester:
            _logger.error('Requester not found. rewardID: %s', rewardID)
            return 0
        return requester.getRemainingValues() or 0

    def __getSerialRewardLeftCount(self, rewardID):
        numberRequester = self.__numberRequesters.get(rewardID, None)
        if not numberRequester or not numberRequester.isDataAvailable():
            return 0
        remainingValuesCount = numberRequester.getRemainingValues()
        givenValuesCount = numberRequester.getGivenValues() or 0
        rewardLimit = self.getRewardLimit(rewardID=rewardID)
        if remainingValuesCount > rewardLimit:
            _logger.error('Remaining values count cannot exceed reward limit!')
            return 0
        elif remainingValuesCount < rewardLimit / 2.0:
            return remainingValuesCount
        elif givenValuesCount > rewardLimit:
            _logger.error('Given values count cannot exceed reward limit!')
            return 0
        else:
            return rewardLimit - givenValuesCount

    @serverSettingsChangeListener(RESOURCE_WELL_GAME_PARAMS_KEY)
    def __onServerSettingsChanged(self, diff):
        self.__currentPurchaseMode = None
        if self.__config is not None:
            self.__config = self.__config.replace(diff[RESOURCE_WELL_GAME_PARAMS_KEY])
        if self.isActive():
            self.__initNumberRequesters(withStart=True)
        else:
            self.stopNumberRequesters()
        self.__onEventUpdated()
        self.onSettingsChanged()
        return

    def __onClientUpdated(self, diff, _):
        if RESOURCE_WELL_PDATA_KEY not in diff:
            return
        self.__syncData.update(diff)
        if 'initialAmounts' in diff[RESOURCE_WELL_PDATA_KEY]:
            self.__setNumberInitialValues()
        self.onEventUpdated()

    def __onTokensUpdated(self, diff):
        if getForbiddenAccountToken(resourceWell=self) in diff:
            self.onEventUpdated()

    def __onRequesterUpdated(self):
        self.onNumberRequesterUpdated()

    def __onEventUpdated(self):
        self.__setNumberInitialValues()
        if self.__notifier is not None:
            self.__notifier.startNotification()
        return

    def __stop(self):
        self._unsubscribe()
        for requester in self.__numberRequesters.values():
            requester.onUpdated -= self.__onRequesterUpdated

        self.stopNumberRequesters()
        if self.__notifier is not None:
            self.__notifier.stopNotification()
        return

    def __clear(self):
        self.__clearNumberRequesters()
        self.__syncData.clear()
        self.__config = None
        self.__currentPurchaseMode = None
        if self.__notifier is not None:
            self.__notifier.clear()
            self.__notifier = None
        return

    def __clearNumberRequesters(self):
        wasActive = False
        for requester in self.__numberRequesters.values():
            wasActive |= requester.isActive
            requester.stop()
            requester.clear()

        self.__numberRequesters.clear()
        return wasActive

    def __initNumberRequesters(self, withStart=False):
        wasActive = self.__clearNumberRequesters()
        for rewardID in self.config.rewards.keys():
            self.__numberRequesters[rewardID] = requester = ResourceWellNumberRequester(rewardID)
            requester.onUpdated += self.__onRequesterUpdated
            if withStart and wasActive:
                requester.start()

    def __setNumberInitialValues(self):
        if self.config.rewards:
            for rewardID, requester in self.__numberRequesters.items():
                requester.setInitialValues(self.__getInitialRemainingValues(rewardID=rewardID))

    def __getInitialRemainingValues(self, rewardID):
        initialAmountsInCache = self.__syncData.getInitialNumberAmounts().get(self.getRewardSequence(rewardID))
        return initialAmountsInCache if initialAmountsInCache == 0 else self.getRewardLimit(rewardID)

    def __createConfig(self):
        return makeTupleByDict(ResourceWellConfig, self.__lobbyContext.getServerSettings().getSettings().get(RESOURCE_WELL_GAME_PARAMS_KEY, {}))
