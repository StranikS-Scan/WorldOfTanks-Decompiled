# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/server_events/game_event/front_progress.py
import logging
import typing
from helpers import dependency
import HBAccountSettings
from gui.server_events.bonuses import mergeBonuses
from historical_battles_common.hb_constants_extension import FRONT_QUEUE_TYPES
from helpers import time_utils
from historical_battles.gui.prb_control.entities.pre_queue.entity import HistoricalBattlesEntity
from historical_battles.gui.server_events.game_event.game_event_progress import ProgressItemsController, GameEventProgress
from historical_battles.gui.server_events.game_event.hb_subdivision_item import HBSubdivisionItemController
from dossiers2.custom.records import DB_ID_TO_RECORD
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.lobby_context import ILobbyContext
from historical_battles_common.hb_constants import HB_GAME_PARAMS_KEY, AccountSettingsKeys
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, Optional
_logger = logging.getLogger(__name__)
_SPECIAL_ACHIEVMENTS = set()
_ACHIEVMENTS_DELETE_FROM_POPUPS = set((aID for aID, (_, name) in DB_ID_TO_RECORD.iteritems() if name in _SPECIAL_ACHIEVMENTS))

class FrontsProgressController(ProgressItemsController):
    _gameEventController = dependency.descriptor(IGameEventController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(FrontsProgressController, self).__init__()
        self.__cachedSelectedSubdivisionIds = {}

    def getCachedSelectedSubdivisionId(self, frontId):
        return self.__cachedSelectedSubdivisionIds.get(frontId)

    def setCachedSelectedSubdivisionId(self, frontId, selectedSubdivisionId):
        self.__cachedSelectedSubdivisionIds[frontId] = selectedSubdivisionId

    def clearCache(self):
        self.__cachedSelectedSubdivisionIds.clear()

    def getInstanceClass(self):
        return FrontProgress

    def _getConfig(self):
        settings = self._lobbyContext.getServerSettings().getSettings()
        return settings.get(HB_GAME_PARAMS_KEY, {})

    def getFrontConfig(self, frontID):
        return self.getFrontsConfig().get(frontID)

    def getFrontsConfig(self):
        return self._getConfig().get('fronts', {})

    def getActiveItemIDs(self):
        return self.getFrontsConfig().keys()

    def getSortedItems(self):
        fronts = self.getItems()
        defence = [ front for front in fronts.values() if front.getName() == 'defence' ]
        offence = [ front for front in fronts.values() if front.getName() == 'offence' ]
        return defence + offence

    def getLatestFront(self):
        latestFront = None
        for front in self.getSortedItems():
            if front.isAvailable():
                latestFront = front

        return latestFront

    def getFronts(self):
        return self.getItems()

    def getFront(self, frontId):
        return self.getFronts().get(frontId)

    def getSelectedFront(self):
        return self.getFront(self.getSelectedFrontID())

    def getSelectedFrontID(self):
        frontSettings = HBAccountSettings.getSettings(AccountSettingsKeys.HISTORICAL_BATTLES_FRONTS)
        return frontSettings[AccountSettingsKeys.SELECTED_HISTORICAL_BATTLES_FRONT]

    def getAllSubdivisionsForSelectedFront(self):
        return self.getSelectedFront().getAllSubdivisions()

    def setSelectedFrontID(self, frontID):
        frontSettings = HBAccountSettings.getSettings(AccountSettingsKeys.HISTORICAL_BATTLES_FRONTS)
        settingsChanged = False
        lastID = frontSettings[AccountSettingsKeys.SELECTED_HISTORICAL_BATTLES_FRONT]
        selectedFrontChanged = lastID != frontID
        if selectedFrontChanged:
            frontSettings[AccountSettingsKeys.SELECTED_HISTORICAL_BATTLES_FRONT] = frontID
            settingsChanged = True
        seenFronts = frontSettings[AccountSettingsKeys.SEEN_HISTORICAL_BATTLES_FRONTS]
        if not seenFronts.get(frontID, False) and self.getFront(frontID).isAvailable():
            seenFronts[frontID] = True
            settingsChanged = True
        if settingsChanged:
            HBAccountSettings.setSettings(AccountSettingsKeys.HISTORICAL_BATTLES_FRONTS, frontSettings)
        if selectedFrontChanged:
            if isinstance(self._gameEventController.prbEntity, HistoricalBattlesEntity):
                self._gameEventController.prbEntity.updateEntityType()
            self._gameEventController.onSelectedFrontChanged()

    def getFrontByName(self, frontName):
        front = next((front for front in self.getFronts().itervalues() if front.getName() == frontName), None)
        if front is None:
            message = 'Cant get frontID - unknown frontName {}'.format(frontName)
            _logger.error(message)
        return front

    def getFrontIdByName(self, frontName):
        front = self.getFrontByName(frontName)
        return front.getID()

    def getFrontBySubdivisionId(self, subdivId):
        for front in self.getFronts().itervalues():
            for id in front.getAllSubdivisions().iterkeys():
                if id == subdivId:
                    return front

        return None

    def getOrderedFrontsList(self):
        return self.getSortedItems()

    def getFrontByID(self, frontID):
        front = self.getFronts().get(frontID, None)
        if front is None:
            message = 'Cant get frontName - unknown frontID {}'.format(frontID)
            _logger.error(message)
        return front

    def getFrontByCoinName(self, coinName):
        front = next((front for front in self.getFronts().values() if front.getCoinsName() == coinName), None)
        if front is None:
            message = 'Cant get frontID - unknown coinName {}'.format(coinName)
            _logger.error(message)
        return front

    def isFrontSeen(self, frontID):
        frontSettings = HBAccountSettings.getSettings(AccountSettingsKeys.HISTORICAL_BATTLES_FRONTS)
        return frontSettings[AccountSettingsKeys.SEEN_HISTORICAL_BATTLES_FRONTS].get(frontID, False)

    def setIsFrontSeen(self, frontID, isFrontSeen):
        frontSettings = HBAccountSettings.getSettings(AccountSettingsKeys.HISTORICAL_BATTLES_FRONTS)
        seenFronts = frontSettings[AccountSettingsKeys.SEEN_HISTORICAL_BATTLES_FRONTS]
        seenFronts[frontID] = isFrontSeen
        HBAccountSettings.setSettings(AccountSettingsKeys.HISTORICAL_BATTLES_FRONTS, frontSettings)

    def getAllSubdivisions(self, frontID):
        return self.getFront(frontID).getAllSubdivisions()

    def getSubdivisionById(self, subdivisionId):
        for front in self.getFronts().values():
            for subDiv in front.getAllSubdivisions().values():
                if subDiv.getID() == subdivisionId:
                    return subDiv

        return None

    def getSelectedSubdivision(self):
        return self.getSelectedFront().getSelectedSubdivision()

    def getSelectedSubdivisionID(self):
        return self.getFront(self.getSelectedFrontID()).getSelectedSubdivisionID()

    def setSelectedSubdivisionID(self, divisionID):
        self.getSelectedFront().setSelectedSubdivisionID(divisionID)
        frontID = self.getSelectedFrontID()
        settings = HBAccountSettings.getSettings(AccountSettingsKeys.SELECTED_HB_DIVISION)
        lastDivisionID = settings.get(frontID)
        if lastDivisionID != divisionID:
            settings[frontID] = divisionID
            HBAccountSettings.setSettings(AccountSettingsKeys.SELECTED_HB_DIVISION, settings)

    def getProgresses(self):
        return self.__itemsCache.items.historicalBattles.subdivisionsProgressEXP

    @property
    def currentFrontProgressionTokenID(self):
        coinsName = self.getFrontConfig(self.getSelectedFrontID())['frontName']
        return self._gameEventController.coins.getTokenName(coinsName)


class FrontProgress(GameEventProgress):
    _gameEventController = dependency.descriptor(IGameEventController)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, frontID):
        self._id = frontID
        super(FrontProgress, self).__init__('se22_front_{}'.format(self.getQuestID()), 'progress', 'final_reward', 'bonuses', 'se22_front_{}_bought_last_level'.format(self.getQuestID()))
        self._subdivisions = HBSubdivisionItemController(frontID)

    def __eq__(self, other):
        if isinstance(other, GameEventProgress):
            return self._id == other.getID()
        _logger.error('Cant compare with non GameEventProgress object')

    def init(self):
        super(FrontProgress, self).init()
        self._subdivisions.start()
        self._subdivisions.onItemsUpdated += self._onItemsUpdated
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChanged

    def fini(self):
        self._subdivisions.stop()
        self._subdivisions.onItemsUpdated -= self._onItemsUpdated
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChanged
        super(FrontProgress, self).fini()

    def getID(self):
        return self._id

    def getName(self):
        return self.getConfig().get('frontName')

    def getFrontQueueType(self):
        return FRONT_QUEUE_TYPES.get(self.getName())

    def getQuestID(self):
        return self._id + 1

    def getConfig(self):
        return self._gameEventController.frontController.getFrontConfig(self.getID())

    def getSelectedSubdivision(self):
        allItems = self._subdivisions.getItems()
        return allItems[self._subdivisions.getSelectedSubdivisionID()]

    def setSelectedSubdivisionID(self, value):
        self._subdivisions.setSelectedSubdivisionID(value)

    def getAllSubdivisions(self):
        return self._subdivisions.getItems()

    def getProgressTokenName(self):
        return 'se22_front_{}_event_points'.format(self.getQuestID())

    def getBonuses(self):
        if not self.getItems():
            return []
        bonuses = [ bonus for item in self.getItems() for bonus in item.getBonuses() ]
        return mergeBonuses(bonuses)

    def isEnabled(self):
        return self.getConfig().get('enabled', False)

    def getStartTime(self):
        return self.getConfig().get('startDate')

    def getCoinsName(self):
        return self.getConfig().get('frontName')

    def getProgressionTokenName(self):
        return self._gameEventController.coins.getTokenName(self.getCoinsName())

    def _onItemsUpdated(self, itemID):
        self.onItemsUpdated()

    def __onSettingsChanged(self, diff):
        if HB_GAME_PARAMS_KEY not in diff:
            return
        self._onSyncCompleted()

    def isAvailable(self):
        return self.isEnabled() and time_utils.getTimeDeltaFromNow(self.getStartTime()) <= 0
