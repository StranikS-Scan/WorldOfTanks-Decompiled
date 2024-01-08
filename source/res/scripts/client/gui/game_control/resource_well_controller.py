# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/resource_well_controller.py
import logging
import typing
from Event import Event, EventManager
from PlayerEvents import g_playerEvents
from constants import Configs
from gui.resource_well.number_requester import ResourceWellNumberRequester
from gui.resource_well.resource_well_constants import RESOURCE_WELL_PDATA_KEY
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils
from helpers.events_handler import EventsHandler
from helpers.server_settings import serverSettingsChangeListener
from shared_utils import first, findFirst
from skeletons.gui.game_control import IResourceWellController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, Optional
    from helpers.server_settings import ResourceWellConfig
_logger = logging.getLogger(__name__)

class ResourceWellController(IResourceWellController, EventsHandler):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__eventsManager = EventManager()
        self.onEventUpdated = Event(self.__eventsManager)
        self.onSettingsChanged = Event(self.__eventsManager)
        self.onNumberRequesterUpdated = Event(self.__eventsManager)
        self.onEventStateChanged = Event(self.__eventsManager)
        self.__notifier = SimpleNotifier(self.__getTimeLeft, self.__onEventStateChange)
        self.__serialNumberRequester = ResourceWellNumberRequester(True)
        self.__regularNumberRequester = ResourceWellNumberRequester(False)

    def onLobbyInited(self, event):
        self._subscribe()
        self.__notifier.startNotification()
        self.__setNumberInitialValues()

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__serialNumberRequester.clear()
        self.__regularNumberRequester.clear()
        self.__stop()

    def fini(self):
        self.__eventsManager.clear()
        self.__serialNumberRequester.clear()
        self.__regularNumberRequester.clear()
        self.__stop()

    def isEnabled(self):
        return self.__getConfig().isEnabled

    def isActive(self):
        return self.isEnabled() and self.isStarted() and not self.isFinished()

    def isStarted(self):
        return self.getStartTime() <= time_utils.getServerUTCTime()

    def isFinished(self):
        return self.getFinishTime() <= time_utils.getServerUTCTime()

    def isNotStarted(self):
        return self.isEnabled() and not self.isStarted()

    def isPaused(self):
        return not self.isEnabled() and self.isStarted() and not self.isFinished()

    def getSeason(self):
        return self.__getConfig().season

    def getRewardLimit(self, isTop):
        return findFirst(lambda reward: reward.isSerial == isTop, self.__getConfig().rewards.itervalues()).limit

    def getFinishTime(self):
        return self.__getConfig().finishTime

    def getStartTime(self):
        return self.__getConfig().startTime

    def getCurrentPoints(self):
        return self.__itemsCache.items.resourceWell.getCurrentPoints()

    def getMaxPoints(self):
        return self.__getConfig().points

    def getRewardVehicle(self):
        return first(first(self.__getConfig().rewards.itervalues()).bonus.get('vehicles', {}).keys())

    def getRewardStyleID(self):
        topReward = findFirst(lambda reward: reward.isSerial, self.__getConfig().rewards.itervalues())
        return first(topReward.bonus['vehicles'].values())['customization'].get('styleId', 0)

    def getRewardSequence(self, isTop):
        return findFirst(lambda reward: reward.isSerial == isTop, self.__getConfig().rewards.itervalues()).sequence

    def getRewardLeftCount(self, isTop):
        return (self.__getSerialRewardLeftCount() if isTop else self.__getRegularRewardLeftCount()) or 0

    def isRewardEnabled(self, isTop):
        topRewardLeftCount = self.getRewardLeftCount(isTop=True)
        return isTop and topRewardLeftCount or not (isTop or topRewardLeftCount)

    def isRewardCountAvailable(self, isTop=True):
        requester = self.__serialNumberRequester if isTop else self.__regularNumberRequester
        return requester.isDataAvailable()

    def getReminderTime(self):
        return self.__getConfig().remindTime

    def isCompleted(self):
        return self.__itemsCache.items.resourceWell.getReward() is not None

    def getResources(self):
        return self.__getConfig().resources

    def getRewards(self):
        return self.__getConfig().rewards

    def getRewardID(self, isTop):
        return findFirst(lambda (rewardID, reward): reward.isSerial == isTop, self.getRewards().iteritems())[0]

    def startNumberRequesters(self):
        if self.isEnabled():
            self.__setNumberInitialValues()
            self.__serialNumberRequester.start()
            self.__regularNumberRequester.start()

    def stopNumberRequesters(self):
        self.__serialNumberRequester.stop()
        self.__regularNumberRequester.stop()

    def _getEvents(self):
        return ((self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),
         (self.__serialNumberRequester.onUpdated, self.__onRequesterUpdated),
         (self.__regularNumberRequester.onUpdated, self.__onRequesterUpdated),
         (g_playerEvents.onClientUpdated, self.__onClientUpdated))

    def __getConfig(self):
        return self.__lobbyContext.getServerSettings().resourceWellConfig

    def __getTimeLeft(self):
        if not self.isStarted():
            return max(0, self.getStartTime() - time_utils.getServerUTCTime())
        return max(0, self.getFinishTime() - time_utils.getServerUTCTime()) if not self.isFinished() else 0

    def __onEventStateChange(self):
        self.onEventUpdated()
        self.onEventStateChanged()

    def __getRegularRewardLeftCount(self):
        return self.__regularNumberRequester.getRemainingValues() or 0

    def __getSerialRewardLeftCount(self):
        if not self.__serialNumberRequester.isDataAvailable():
            return 0
        remainingValuesCount = self.__serialNumberRequester.getRemainingValues()
        givenValuesCount = self.__serialNumberRequester.getGivenValues() or 0
        rewardLimit = self.getRewardLimit(True)
        if remainingValuesCount > rewardLimit:
            _logger.error('Remaining values count cannot exceed reward limit!')
            return 0
        if remainingValuesCount < rewardLimit / 2.0:
            return remainingValuesCount
        if givenValuesCount > rewardLimit:
            _logger.error('Given values count cannot exceed reward limit!')
            return 0
        return rewardLimit - givenValuesCount

    def __getInitialRemainingValues(self, isSerial):
        initialAmountsInCache = self.__itemsCache.items.resourceWell.getInitialNumberAmounts().get(self.getRewardSequence(isSerial))
        return initialAmountsInCache if initialAmountsInCache == 0 else self.getRewardLimit(isSerial)

    @serverSettingsChangeListener(Configs.RESOURCE_WELL.value)
    def __onServerSettingsChanged(self, diff):
        resourceWellDiff = diff[Configs.RESOURCE_WELL.value]
        if 'finishTime' in resourceWellDiff or 'startTime' in resourceWellDiff:
            self.__onEventUpdated()
        if 'isEnabled' in resourceWellDiff:
            self.__onEventUpdated()
        if not self.isActive():
            self.stopNumberRequesters()
        self.onSettingsChanged()

    def __onClientUpdated(self, diff, _):
        isRemaining = self.__serialNumberRequester.getValuesLeft() is not None and self.__regularNumberRequester.getValuesLeft() is not None
        if RESOURCE_WELL_PDATA_KEY in diff and 'initialAmounts' in diff[RESOURCE_WELL_PDATA_KEY] and not isRemaining:
            self.__setNumberInitialValues()
        return

    def __onRequesterUpdated(self):
        self.onNumberRequesterUpdated()

    def __onEventUpdated(self):
        self.__setNumberInitialValues()
        self.__notifier.startNotification()
        self.onEventUpdated()

    def __stop(self):
        self._unsubscribe()
        self.__notifier.stopNotification()
        self.stopNumberRequesters()

    def __setNumberInitialValues(self):
        if self.__getConfig().rewards:
            self.__serialNumberRequester.setInitialValues(self.__getInitialRemainingValues(isSerial=True))
            self.__regularNumberRequester.setInitialValues(self.__getInitialRemainingValues(isSerial=False))
