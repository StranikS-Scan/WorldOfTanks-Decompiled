# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/collective_goal_entry_point_controller.py
import bisect
import json
import logging
import typing
from Event import EventManager, EventsSubscriber, Event
from bootcamp.BootCampEvents import g_bootcampEvents
from constants import Configs
from gui.shared.utils.requesters.collective_goal_requester import CollectiveGoalRequester
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils, getLocalizedData
from skeletons.gui.game_control import ICollectiveGoalEntryPointController, IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from helpers.server_settings import serverSettingsChangeListener
if typing.TYPE_CHECKING:
    from helpers.server_settings import _CollectiveGoalEntryPointConfig
_logger = logging.getLogger(__name__)
_DEFAULTS = {'currentPoints': 0,
 'startDate': 0,
 'endDate': 0,
 'discounts': {}}

class CollectiveGoalEntryPointController(ICollectiveGoalEntryPointController):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __bootcamp = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(CollectiveGoalEntryPointController, self).__init__()
        self.__eventsManager = EventManager()
        self.__eventsSubscriber = EventsSubscriber()
        self.__requester = CollectiveGoalRequester()
        self.__notifier = SimpleNotifier(self.__getTimeLeft, self.__onEventStatusChanged)
        self.__data = _DEFAULTS
        self.onDataUpdated = Event(self.__eventsManager)
        self.onEventUpdated = Event(self.__eventsManager)
        self.onSettingsChanged = Event(self.__eventsManager)

    def init(self):
        g_bootcampEvents.onBootcampStarted += self.__onEnterBootcamp

    def onLobbyInited(self, event):
        self.__eventsSubscriber.subscribeToEvent(self.__requester.onUpdated, self.__onRequesterUpdated)
        self.__eventsSubscriber.subscribeToEvent(self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged)
        self.__startRequester()
        self.__notifier.startNotification()

    def onAccountBecomeNonPlayer(self):
        self.__eventsSubscriber.unsubscribeFromAllEvents()
        self.__requester.stop()
        self.__notifier.stopNotification()

    def fini(self):
        g_bootcampEvents.onBootcampStarted -= self.__onEnterBootcamp
        self.__eventsSubscriber.unsubscribeFromAllEvents()
        self.__requester.clear()
        self.__eventsManager.clear()
        self.__notifier.stopNotification()
        self.__notifier.clear()
        self.__data = _DEFAULTS

    def isEnabled(self):
        serverTime = time_utils.getServerUTCTime()
        config = self.__getConfig()
        return config.isEnabled and config.startTime <= serverTime <= config.finishTime and not self.__bootcamp.isInBootcamp()

    def isStarted(self):
        serverTime = time_utils.getServerUTCTime()
        startTime = self.getActivePhaseStartTime()
        return startTime <= serverTime if startTime else False

    def isFinished(self):
        serverTime = time_utils.getServerUTCTime()
        finishTime = self.getActivePhaseFinishTime()
        return finishTime < serverTime if finishTime else False

    def isCompleted(self):
        discounts = self.__data['discounts']
        return self.__data['currentPoints'] >= max(discounts.keys()) if discounts else False

    def isForbidden(self):
        return not self.__data['discounts'] or self.__data['currentPoints'] < 0

    def getEventStartTime(self):
        return self.__getConfig().startTime

    def getEventFinishTime(self):
        return self.__getConfig().finishTime

    def getMarathonPrefix(self):
        return self.__getConfig().marathonPrefix

    def getActivePhaseStartTime(self):
        return self.__data['startDate']

    def getActivePhaseFinishTime(self):
        return self.__data['endDate']

    def getCurrentPoints(self):
        return self.__data['currentPoints']

    def getStagePoints(self):
        currentPoints = self.getCurrentPoints()
        discounts = self.getDiscounts()
        if not discounts:
            return 0
        points = sorted(discounts.keys())
        ind = bisect.bisect_right(points, currentPoints, 0, len(points) - 1)
        left = points[ind - 1] if ind > 0 else 0
        right = points[ind]
        return (currentPoints - left, right - left)

    def getDiscounts(self):
        return self.__data['discounts']

    def getCurrentDiscount(self):
        discounts = self.__data['discounts']
        if not discounts:
            return (-1, None)
        else:
            currentPoints = self.__data['currentPoints']
            points = sorted(discounts.keys())
            ind = bisect.bisect_right(points, currentPoints, 0, len(points) - 1)
            return (ind + 1, discounts[points[ind]])

    def getMarathonName(self):
        return getLocalizedData({'marathonName': self.__getConfig().marathonName}, 'marathonName')

    def getGoalType(self):
        return self.__getConfig().goalType

    def getGoalDescription(self):
        return getLocalizedData({'goalDescription': self.__getConfig().goalDescription}, 'goalDescription')

    def getRulesCaption(self):
        return getLocalizedData({'rulesCaption': self.__getConfig().rulesCaption}, 'rulesCaption')

    def __getConfig(self):
        return self.__lobbyContext.getServerSettings().collectiveGoalEntryPointConfig

    def __startRequester(self):
        if self.isEnabled():
            self.__requester.start(self.__getConfig().hermodChannelName)

    def __getTimeLeft(self):
        serverTime = time_utils.getServerUTCTime()
        config = self.__getConfig()
        if serverTime <= config.startTime:
            return config.startTime - serverTime
        if self.__data:
            activePhaseStart = self.getActivePhaseStartTime()
            if activePhaseStart and serverTime <= activePhaseStart:
                return activePhaseStart - serverTime
            activePhaseEnd = self.getActivePhaseFinishTime()
            if activePhaseEnd and serverTime <= activePhaseEnd:
                return activePhaseEnd - serverTime
        return config.finishTime - serverTime if serverTime <= config.finishTime else 0

    def __updateData(self, rawData):
        self.__data['currentPoints'] = rawData.get('currentPoints', _DEFAULTS['currentPoints'])
        self.__data['startDate'] = rawData.get('startDate', _DEFAULTS['startDate'])
        self.__data['endDate'] = rawData.get('endDate', _DEFAULTS['endDate'])
        self.__data['discounts'] = {i.get('points', 0):i.get('discount', 0) for i in rawData.get('discounts', [])}

    def __onRequesterUpdated(self):
        message = self.__requester.getMessage()
        if message:
            try:
                message = json.loads(message)
                oldStartDate = self.__data['startDate']
                oldEndDate = self.__data['endDate']
                self.__updateData(message)
                if self.__data['startDate'] != oldStartDate or self.__data['endDate'] != oldEndDate:
                    self.__notifier.startNotification()
                    self.__onEventStatusChanged()
                self.onDataUpdated()
            except ValueError:
                _logger.error('Invalid JSON data received from service')

    def __onEventStatusChanged(self):
        self.onEventUpdated()

    @serverSettingsChangeListener(Configs.COLLECTIVE_GOAL_ENTRY_POINT_CONFIG.value)
    def __onServerSettingsChanged(self, diff):
        collectiveGoalDiff = diff[Configs.COLLECTIVE_GOAL_ENTRY_POINT_CONFIG.value]
        if self.__requester.isActive:
            if not self.isEnabled():
                self.__requester.stop()
                self.__data = _DEFAULTS
            elif 'hermodChannelName' in collectiveGoalDiff:
                self.__requester.stop()
                self.__startRequester()
        elif self.isEnabled():
            self.__startRequester()
        if self.__getConfig().isEnabled and ('startTime' in collectiveGoalDiff or 'finishTime' in collectiveGoalDiff):
            self.__notifier.startNotification()
        if {'isEnabled', 'startTime', 'finishTime'}.intersection(collectiveGoalDiff):
            self.__onEventStatusChanged()
        self.onSettingsChanged()

    def __onEnterBootcamp(self):
        if self.__requester.isActive:
            self.__requester.stop()
