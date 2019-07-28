# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/game_event_controller.py
from functools import partial
import logging
from constants import GLOBAL_ENERGY_ID
from Event import Event, EventManager
from gui.prb_control.events_dispatcher import g_eventDispatcher
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from general import GeneralProgress
from award_window_controller import GameEventAwardWindowController
from energy import GameEventEnergy
from front_progress import FrontProgress
from wotdecorators import condition
from PlayerEvents import g_playerEvents
from gui.prb_control import prbDispatcherProperty
from generals_history_info import GeneralsHistoryInfo
from battle_results import BattleResults
_SNDID_ACHIEVEMENT = 'result_screen_achievements'
_GENERAL_DAILY_QUESTS_GROUP_ID = 'se1_2019_energy'
_GAME_EVENT_GENERALS_DATA_STORAGE_KEY = 'generals'
_GAME_EVENT_FRONTS_DATA_STORAGE_KEY = 'fronts'
_logger = logging.getLogger(__name__)

class GameEventController(IGameEventController):
    eventsCache = dependency.descriptor(IEventsCache)
    ifStarted = condition('_started')

    def __init__(self):
        super(GameEventController, self).__init__()
        self._generals = GeneralsProgressItemsController()
        self._fronts = FrontsProgressItemsController()
        self._generalsHistoryInfo = GeneralsHistoryInfo()
        self._awardWindowShowController = GameEventAwardWindowController(self)
        self._energy = GameEventEnergy(GLOBAL_ENERGY_ID, _GENERAL_DAILY_QUESTS_GROUP_ID)
        self._battleResults = BattleResults()
        self._em = EventManager()
        self.onProgressChanged = Event(self._em)
        self.onSelectedGeneralChanged = Event(self._em)
        self._selectedGeneralID = None
        self._started = False
        return

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def init(self):
        pass

    def fini(self):
        self._em.clear()
        self.stop()

    def getGeneralsHistoryInfo(self):
        return self._generalsHistoryInfo

    def getSelectedGeneralID(self):
        if self._selectedGeneralID is None and self.getGenerals():
            self.setSelectedGeneralID(sorted(self.getGenerals().keys())[0])
        return self._selectedGeneralID

    def getSelectedGeneral(self):
        generalID = self.getSelectedGeneralID()
        if generalID is None:
            return
        else:
            general = self.getGeneral(generalID)
            return general

    def setSelectedGeneralID(self, generalID):
        if not self.getGenerals():
            return
        if self._selectedGeneralID == generalID:
            return
        if generalID not in self.getGenerals():
            _logger.error('Unknown generalID "%s"', generalID)
            return
        self._selectedGeneralID = generalID
        self.onSelectedGeneralChanged()
        g_eventDispatcher.updateUI()

    def getAvailableGeneralIDs(self):
        return self.getGenerals().keys()

    def getBattleResultsInfo(self):
        return self._battleResults

    def start(self):
        if self._started:
            _logger.error('GameEventController already started')
            return
        for container in self._getContainers():
            container.start()

        self._started = True
        g_playerEvents.onGeneralLockChanged += self._onGeneralLockChanged
        self._generals.onItemsUpdated += self._onProgressChanged
        self._fronts.onItemsUpdated += self._onProgressChanged
        self._onProgressChanged()

    @ifStarted
    def stop(self):
        g_playerEvents.onGeneralLockChanged -= self._onGeneralLockChanged
        self._generals.onItemsUpdated -= self._onProgressChanged
        self._fronts.onItemsUpdated -= self._onProgressChanged
        for container in self._getContainers():
            container.stop()

        self._em.clear()
        self._started = False

    def clear(self):
        self.stop()

    def getGenerals(self):
        return self._generals.getItems()

    def getGeneral(self, generalId):
        return self.getGenerals().get(generalId)

    def getEnergy(self):
        return self._energy

    def getFronts(self):
        return self._fronts.getItems()

    def getFront(self, frontID):
        return self.getFronts().get(frontID)

    def isEnabled(self):
        return self.eventsCache.isEventEnabled()

    def _getContainers(self):
        return (self._generals,
         self._fronts,
         self._energy,
         self._awardWindowShowController,
         self._generalsHistoryInfo,
         self._battleResults)

    def _onProgressChanged(self, *args, **kwargs):
        self.onProgressChanged()

    def _onGeneralLockChanged(self):
        if self.prbDispatcher is not None:
            g_eventDispatcher.updateUI()
        return


class ProgressItemsController(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(ProgressItemsController, self).__init__()
        self._container = None
        self._em = EventManager()
        self.onItemsUpdated = Event(self._em)
        return

    def start(self):
        self._container = {}
        self.eventsCache.onSyncCompleted += self._onSyncCompleted
        self._onSyncCompleted()

    def stop(self):
        self.eventsCache.onSyncCompleted -= self._onSyncCompleted
        keysCopy = self._container.keys()
        for itemID in keysCopy:
            self._removeProgressItem(itemID)

        self._container = None
        self._em.clear()
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
        for frontID in unusedIDs:
            self._removeProgressItem(frontID)

        for frontID in activeIDs:
            self._addProgressItem(frontID)

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


class GeneralsProgressItemsController(ProgressItemsController):

    def getInstanceClass(self):
        return GeneralProgress

    def getActiveItemIDs(self):
        return self.eventsCache.getGameEventData().get(_GAME_EVENT_GENERALS_DATA_STORAGE_KEY, {}).keys()


class FrontsProgressItemsController(ProgressItemsController):

    def getInstanceClass(self):
        return FrontProgress

    def getActiveItemIDs(self):
        return self.eventsCache.getGameEventData().get(_GAME_EVENT_FRONTS_DATA_STORAGE_KEY, [])
