# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/game_event_controller.py
import logging
import time
from functools import partial
from typing import Dict, Tuple, Generator, Set
from Event import Event, EventManager
from account_helpers import AccountSettings
from account_helpers.AccountSettings import SECRET_EVENT_BERLIN_TAB_2020_SEEN, SECRET_EVENT_INTRO_ANIMATION_SEEN
from commander_event_progress import CommanderEventProgress
from constants import LONG_WAIT_QUEUE_TIME
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.server_events.game_event.award_window_controller import GameEventAwardWindowController
from gui.server_events.game_event.chat_controller import ChatConntroller
from gui.server_events.game_event.energy import GameEventEnergy
from gui.server_events.game_event.event_hangar_sound_controller import EventHangarSoundController
from gui.server_events.game_event.front_progress import FrontProgress
from gui.server_events.game_event.hero_tank import EventHeroTank
from helpers import dependency, time_utils
from shared_utils import first
from shop import Shop
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from wotdecorators import condition
_ENERGY_DAILY_QUESTS_GROUP_ID = 'se_2020_energy'
_logger = logging.getLogger(__name__)

class GameEventController(IGameEventController):
    eventsCache = dependency.descriptor(IEventsCache)
    bootcampController = dependency.descriptor(IBootcampController)
    ifStarted = condition('_started')

    def __init__(self):
        super(GameEventController, self).__init__()
        self._commanders = CommandersProgressItemsController()
        self._fronts = FrontsProgressItemsController()
        self._awardWindowShowController = GameEventAwardWindowController(self)
        self._chatController = ChatConntroller()
        self._energy = GameEventEnergy(_ENERGY_DAILY_QUESTS_GROUP_ID)
        self._shop = Shop()
        self._heroTank = EventHeroTank()
        self._hangarSoundController = EventHangarSoundController()
        self._em = EventManager()
        self.onProgressChanged = Event(self._em)
        self.onSelectedCommanderChanged = Event(self._em)
        self.onEventFinished = Event(self._em)
        self._selectedCommanderID = 0
        self._started = False
        self._bannerAnimationShown = False

    def init(self):
        pass

    def fini(self):
        self._em.clear()
        self.stop()

    def getSelectedCommanderID(self):
        if self._selectedCommanderID is None and self.getCommanders():
            self.setSelectedCommanderID(sorted(self.getCommanders().keys())[0])
        return self._selectedCommanderID

    def getCommanderByEnergy(self, energyID):
        commander = first((commander for commander in self.getCommanders().itervalues() if energyID in commander.energies), None)
        if commander is None:
            logging.error('Cannot find commander by energyID %s. There must be some desync between data on server and client', energyID)
        return commander

    def getSelectedCommander(self):
        commanderID = self.getSelectedCommanderID()
        if commanderID is None:
            return
        else:
            commander = self.getCommander(commanderID)
            return commander

    def setSelectedCommanderID(self, commanderID):
        if not self.getCommanders():
            return
        if self._selectedCommanderID == commanderID:
            return
        if commanderID not in self.getCommanders():
            _logger.error('Unknown commanderID "%s"', commanderID)
            return
        self._selectedCommanderID = commanderID
        self.onSelectedCommanderChanged()
        g_eventDispatcher.updateUI()

    def getAvailableCommanderIDs(self):
        return self.getCommanders().keys()

    def start(self):
        if self.bootcampController.isInBootcamp():
            return
        if self._started:
            _logger.error('GameEventController already started')
            return
        for container in self._getContainers():
            container.start()

        self._started = True
        self._commanders.onItemsUpdated += self._onProgressChanged
        self._onProgressChanged()

    @ifStarted
    def stop(self):
        self._commanders.onItemsUpdated -= self._onProgressChanged
        for container in self._getContainers():
            container.stop()

        self._em.clear()
        self._started = False

    def clear(self):
        self.stop()

    def getCommanders(self):
        return self._commanders.getItems()

    def getEnergy(self):
        return self._energy

    def getCommander(self, commanderId):
        return self.getCommanders().get(commanderId)

    def getFronts(self):
        return self._fronts.getItems()

    def getCurrentFront(self):
        return self.getFront(1)

    def istBerlinTabShown(self):
        return AccountSettings.getCounters(SECRET_EVENT_BERLIN_TAB_2020_SEEN)

    def setBerlinTabShown(self, value):
        AccountSettings.setCounters(SECRET_EVENT_BERLIN_TAB_2020_SEEN, value)

    def getFront(self, frontID):
        return self.getFronts().get(frontID)

    def isEnabled(self):
        return self.eventsCache.isEventEnabled()

    def getShop(self):
        return self._shop

    def getHeroTank(self):
        return self._heroTank

    def getBerlinStartTime(self):
        return self.__getDate('dateSpecialAccessForAll')

    def getBerlinStartTimeUTC(self):
        return self.eventsCache.getGameEventData()['dateSpecialAccessForAll']

    def getBerlinStartTimeLeft(self):
        return self.__getTimeDelta(self.getBerlinStartTime())

    def isBerlinStarted(self):
        data = self.eventsCache.getGameEventData()
        return data.get('isBerlinStarted', False)

    def getLongWaitTime(self):
        data = self.eventsCache.getGameEventData()
        return data.get('longWaitTime', LONG_WAIT_QUEUE_TIME)

    def getEventFinishTime(self):
        return self.__getDate('endDate')

    def getEventFinishTimeUTC(self):
        return self.eventsCache.getGameEventData()['endDate']

    def getEventFinishTimeLeft(self):
        return self.__getTimeDelta(self.getEventFinishTime())

    @property
    def wasBannerAnimationShown(self):
        return AccountSettings.getCounters(SECRET_EVENT_INTRO_ANIMATION_SEEN)

    def getCompletedMessages(self, completedQuestIDs, popUps):
        fronts = self.getFronts()
        if fronts:
            for progress in fronts.itervalues():
                for message in self.getCompletedMessagesForProgress(progress, completedQuestIDs, popUps):
                    yield message

        commanders = self.getCommanders()
        if commanders:
            for progress in sorted(commanders.itervalues(), key=lambda item: item.getID()):
                messages = list(self.getCompletedMessagesForProgress(progress, completedQuestIDs, popUps))
                if messages:
                    yield messages[-1]

    def getCompletedMessagesForProgress(self, progress, completedQuestIDs, popUps):
        for item in progress.getItems():
            quest = item.getQuest()
            if quest:
                questID = quest.getID()
                if questID in completedQuestIDs:
                    completedQuestIDs.remove(questID)
                    for message in item.getCompletedMessages(popUps):
                        yield message

    def setBannerAnimationAsShown(self):
        AccountSettings.setCounters(SECRET_EVENT_INTRO_ANIMATION_SEEN, True)

    def _getContainers(self):
        return (self._commanders,
         self._fronts,
         self._shop,
         self._awardWindowShowController,
         self._hangarSoundController,
         self._heroTank,
         self._chatController)

    def _onProgressChanged(self, *args, **kwargs):
        self.onProgressChanged()

    def __getDate(self, settingsName):
        data = self.eventsCache.getGameEventData()
        return time_utils.makeLocalServerTime(data[settingsName]) if data and settingsName in data else time.time()

    def __getTimeDelta(self, finishTime):
        return time_utils.getTimeDeltaFromNowInLocal(finishTime) if finishTime is not None else 0


class ProgressItemsController(object):
    eventsCache = dependency.descriptor(IEventsCache)
    ifStarted = condition('_started')

    def __init__(self):
        super(ProgressItemsController, self).__init__()
        self._container = None
        self._em = EventManager()
        self.onItemsUpdated = Event(self._em)
        self._started = False
        return

    def start(self):
        self._container = {}
        self.eventsCache.onSyncCompleted += self._onSyncCompleted
        self._onSyncCompleted()
        self._started = True

    @ifStarted
    def stop(self):
        self.eventsCache.onSyncCompleted -= self._onSyncCompleted
        keysCopy = self._container.keys()
        for itemID in keysCopy:
            self._removeProgressItem(itemID)

        self._container = None
        self._em.clear()
        self._started = False
        return

    def getItems(self):
        return self._container

    def getInstanceClass(self):
        raise NotImplementedError

    def getActiveItemIDs(self):
        raise NotImplementedError

    def _onSyncCompleted(self):
        activeIDs = self.getActiveItemIDs()
        unusedIDs = [ itemID for itemID in self._container.iterkeys() if itemID not in activeIDs ]
        for commanderId in unusedIDs:
            self._removeProgressItem(commanderId)

        for commanderId in activeIDs:
            self._addProgressItem(commanderId)

    def _addProgressItem(self, itemID):
        if itemID in self._container:
            _logger.debug('Progress item with id %s already exist', itemID)
            return
        item = self.getInstanceClass()(itemID)
        self._container[itemID] = item
        item.init()
        item.onItemsUpdated += partial(self._onItemsUpdated, itemID)

    def _removeProgressItem(self, itemID):
        if itemID not in self._container:
            _logger.error("Progress item with id %s doesn't exist", itemID)
            return
        item = self._container[itemID]
        item.fini()
        self._container.pop(itemID)

    def _onItemsUpdated(self, itemID):
        self.onItemsUpdated(itemID)


class CommandersProgressItemsController(ProgressItemsController):

    def getInstanceClass(self):
        return CommanderEventProgress

    def getActiveItemIDs(self):
        return self.eventsCache.getCommanders().keys()


class FrontsProgressItemsController(ProgressItemsController):

    def getInstanceClass(self):
        return FrontProgress

    def getActiveItemIDs(self):
        return self.eventsCache.getFronts()
