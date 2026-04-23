# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/hb_quests_controller.py
import logging
import sys
import BigWorld
from Event import Event, EventManager
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from historical_battles.gui.server_events.battle_quests.quests_container import getHBQuestsContainer
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.skeletons.gui.quests_controller import IHBQuestsController
_logger = logging.getLogger(__name__)
_UPDATE_DELAY = 10

class HBQuestsController(IHBQuestsController):
    __eventsCache = dependency.descriptor(IEventsCache)
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        super(HBQuestsController, self).__init__()
        self._em = EventManager()
        self.onQuestsUpdated = Event(self._em)
        self.onDailyQuestUpdate = Event(self._em)
        self.__questsContainer = getHBQuestsContainer()
        self.__dailyUpdateCallbackID = None
        return

    def getQuestsContainer(self):
        return self.__questsContainer

    def init(self):
        pass

    def fini(self):
        self._em.clear()

    def onAccountBecomePlayer(self):
        self.__eventsCache.onSyncCompleted += self.__onEventsCacheSyncCompleted
        self.__gameEventController.onSelectedFrontChanged += self.__onSelectedFrontChanged

    def onAccountBecomeNonPlayer(self):
        self.__resetDailyUpdateCallback()
        self.__eventsCache.onSyncCompleted -= self.__onEventsCacheSyncCompleted
        self.__gameEventController.onSelectedFrontChanged -= self.__onSelectedFrontChanged

    def __onEventsCacheSyncCompleted(self):
        self.__initQuestsGroup()
        self.__resetDailyUpdateCallback()
        self.onQuestsUpdated()
        self.__scheduleDailyQuestUpdate()

    def __onSelectedFrontChanged(self):
        self.onQuestsUpdated()

    def __initQuestsGroup(self):
        _ = self.__questsContainer.getQuests()

    def __onDailyQuestUpdateTime(self):
        _logger.info('Daily quest update time reached, notifying and rescheduling')
        self.__dailyUpdateCallbackID = None
        self.onDailyQuestUpdate()
        self.__scheduleDailyQuestUpdate()
        return

    def __scheduleDailyQuestUpdate(self):
        if not self.__gameEventController.isEnabled():
            return
        else:
            quests = self.__questsContainer.getDailyQuests(allowCompleted=True)
            nearestUpdateTime = None
            for _, quest in quests:
                timeToUpdate = quest.getFinishTimeLeft() if quest.isStarted() else quest.getStartTimeLeft()
                if timeToUpdate is not None and timeToUpdate > 0:
                    nearestUpdateTime = min(timeToUpdate, nearestUpdateTime or sys.maxint)

            if not nearestUpdateTime:
                _logger.info('No daily quests with valid update time, skipping schedule')
                return
            delay = nearestUpdateTime + _UPDATE_DELAY
            self.__dailyUpdateCallbackID = BigWorld.callback(delay, self.__onDailyQuestUpdateTime)
            _logger.info('Scheduled daily quest update in %d seconds', delay)
            return

    def __resetDailyUpdateCallback(self):
        if self.__dailyUpdateCallbackID is not None:
            _logger.debug('Cancelling daily quest update callback')
            BigWorld.cancelCallback(self.__dailyUpdateCallbackID)
            self.__dailyUpdateCallbackID = None
        return
