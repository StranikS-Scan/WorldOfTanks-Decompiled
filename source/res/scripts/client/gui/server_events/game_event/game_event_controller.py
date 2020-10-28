# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/game_event_controller.py
from functools import partial
import logging
from gui.server_events.game_event.award_window_controller import GameEventAwardWindowController
from constants import EVENT_CLIENT_DATA
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.gui_items.Vehicle import sortCrew
from Event import Event, EventManager
from account_helpers import AccountSettings
from account_helpers.AccountSettings import EVENT_CURRENT_DIFFICULTY_LEVEL
from gui.server_events.game_event.missions import EventMissions
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from commander_event_progress import CommanderEventProgress
from difficulty_progress import DifficultyEventProgress, DIFFICULTY_LEVEL_TOKEN
from wotdecorators import condition
from items import tankmen
from gui.shared.gui_items.Tankman import Tankman
_logger = logging.getLogger(__name__)

class GameEventController(IGameEventController):
    eventsCache = dependency.descriptor(IEventsCache)
    ifStarted = condition('_started')

    def __init__(self):
        super(GameEventController, self).__init__()
        self._commanders = CommandersProgressItemsController()
        self._difficulty = DifficultyEventProgress()
        self._missions = EventMissions()
        self._awardWindowShowController = GameEventAwardWindowController(self)
        from shop import Shop
        from vehicles_controller import VehiclesController
        self._vehiclesController = VehiclesController()
        self._shop = Shop()
        self._em = EventManager()
        self.onProgressChanged = Event(self._em)
        self.onSelectedDifficultyLevelChanged = Event(self._em)
        self.onQuestsUpdated = Event(self._em)
        self._selectedCommanderID = None
        self._selectedDifficultyLevel = None
        self._squadDifficultyLevel = None
        self._started = False
        return

    def init(self):
        g_clientUpdateManager.addCallbacks({'eventsData.' + str(EVENT_CLIENT_DATA.QUEST): self._onQuestsUpdated})

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._em.clear()
        self.stop()

    def getAvailableCommanderIDs(self):
        return self.getCommanders().keys()

    def getVehiclesController(self):
        return self._vehiclesController

    def start(self):
        if self._started:
            _logger.error('GameEventController already started')
            return
        for container in self._getContainers():
            container.start()

        self.getDifficultyController().init()
        self._started = True
        self._commanders.onItemsUpdated += self._onProgressChanged
        self._onProgressChanged()

    @ifStarted
    def stop(self):
        self._commanders.onItemsUpdated -= self._onProgressChanged
        for container in self._getContainers():
            container.stop()

        self.getDifficultyController().fini()
        self._em.clear()
        self._started = False

    def clear(self):
        self.stop()

    def getCommanders(self):
        return self._commanders.getItems()

    def getCommander(self, commanderId):
        return self.getCommanders().get(commanderId)

    def getVehicleSettings(self):
        return self._vehiclesController.getVehicleSettings()

    def getMissionsController(self):
        return self._missions

    def getDifficultyController(self):
        return self._difficulty

    def isEnabled(self):
        return self.eventsCache.isEventEnabled()

    def getShop(self):
        return self._shop

    def _getContainers(self):
        return (self._commanders,
         self._missions,
         self._shop,
         self._vehiclesController,
         self._awardWindowShowController)

    def _onQuestsUpdated(self, diff):
        self._shop.updateCache()
        self.onQuestsUpdated()

    def _onProgressChanged(self, *args, **kwargs):
        self.onProgressChanged()

    def needEventCrew(self, vehicle):
        return True if vehicle.intCD in self._vehiclesController.getVehiclesForRent() and not vehicle.hasCrew else False

    def getEventCrew(self, vehicle):
        quests = self.eventsCache.getHiddenQuests()
        questId = self._vehiclesController.getVehiclesForRent().get(vehicle.intCD, {}).get('questId', '')
        if questId in quests:
            quest = quests[questId]
            bonuses = quest.getBonuses()
            crew = next((item.getValue().get(vehicle.intCD, {}).get('tankmen') for item in bonuses if item.getName() == 'vehicles' and vehicle.intCD in item.getValue()))
            crewItems = []
            crewRoles = vehicle.descriptor.type.crewRoles
            commanderEffRoleLevel = 0
            vehicle.bonuses['brotherhood'] = tankmen.getSkillsConfig().getSkill('brotherhood').crewLevelIncrease
            for tman in crew:
                if tman is None:
                    vehicle.bonuses['brotherhood'] = 0.0
                    continue
                tdescr = tankmen.TankmanDescr(compactDescr=tman)
                if 'brotherhood' not in tdescr.skills or tdescr.skills.index('brotherhood') == len(tdescr.skills) - 1 and tdescr.lastSkillLevel != tankmen.MAX_SKILL_LEVEL:
                    vehicle.bonuses['brotherhood'] = 0.0
                if tdescr.role == Tankman.ROLES.COMMANDER:
                    factor, addition = tdescr.efficiencyOnVehicle(vehicle.descriptor)
                    commanderEffRoleLevel = round(tdescr.roleLevel * factor + addition)

            vehicle.bonuses['commander'] += round(commanderEffRoleLevel + vehicle.bonuses['brotherhood'])
            idx = 0
            for tman in crew:
                if isinstance(tman, str):
                    crewItems.append((idx, vehicle.itemsFactory.createTankman(tman, vehicle=vehicle)))
                    idx += 1

            return sortCrew(crewItems, crewRoles)
        else:
            return vehicle.getPerfectCrew()

    def getDifficultyLevels(self):
        levels = [ item.getDifficultyLevel() for item in self._difficulty.getItems() ]
        return levels

    def getMaxUnlockedDifficultyLevel(self):
        return max((level for level in self.getDifficultyLevels() if self._difficulty.getItemOnDifficultyLevel(level).isCompleted()))

    def setSelectedDifficultyLevel(self, difficultyLevel, isCommander=False):
        if not self.getDifficultyLevels():
            return
        if self._selectedDifficultyLevel == difficultyLevel:
            return
        if difficultyLevel not in self.getDifficultyLevels():
            _logger.error('Unknown difficultyLevel "%s"', difficultyLevel)
            return
        if not self._difficulty.getItemOnDifficultyLevel(difficultyLevel).isCompleted():
            _logger.info('difficultyLevel "%s" is locked', difficultyLevel)
            return
        self._selectedDifficultyLevel = difficultyLevel
        if isCommander:
            self.setSquadDifficultyLevel(difficultyLevel)
        AccountSettings.setCounters(EVENT_CURRENT_DIFFICULTY_LEVEL, difficultyLevel)
        self.onSelectedDifficultyLevelChanged()
        return True

    def getSelectedDifficultyLevel(self):
        self._selectedDifficultyLevel = AccountSettings.getCounters(EVENT_CURRENT_DIFFICULTY_LEVEL)
        if self._selectedDifficultyLevel is None and self.getDifficultyLevels():
            self.setSelectedDifficultyLevel(self.eventsCache.getDifficultyParams().get('defaultLevel'))
        return self._selectedDifficultyLevel

    def hasDifficultyLevelToken(self, difficultyLevel):
        if difficultyLevel == 1:
            return True
        token = DIFFICULTY_LEVEL_TOKEN.format(difficultyLevel)
        return token in self.eventsCache.questsProgress.getTokensData()

    def getSquadDifficultyLevel(self):
        if self._squadDifficultyLevel is None:
            self.setSquadDifficultyLevel(self.getSelectedDifficultyLevel())
        return self._squadDifficultyLevel

    def setSquadDifficultyLevel(self, level):
        self._squadDifficultyLevel = level
        self.setSelectedDifficultyLevel(level, True)


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
