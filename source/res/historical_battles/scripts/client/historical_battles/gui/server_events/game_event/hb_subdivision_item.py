# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/server_events/game_event/hb_subdivision_item.py
import BigWorld
import logging
import typing
from historical_battles.gui.server_events.game_event.game_event_progress import ProgressItemsController, GameEventCollection
from helpers import dependency
from items import vehicles
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache
from historical_battles_common.helpers_config import getDivisionLevelByExp, getDivisionCurrentLevelMaxExp
if typing.TYPE_CHECKING:
    from Account import Account
_logger = logging.getLogger(__name__)

class HBSubdivisionItemController(ProgressItemsController):
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, frontID):
        super(HBSubdivisionItemController, self).__init__()
        self.frontID = frontID
        self.selectedSubdivisionID = None
        cachedDivisionId = self._gameEventController.frontController.getCachedSelectedSubdivisionId(frontID)
        self.setSelectedSubdivisionID(cachedDivisionId if cachedDivisionId is not None else self.getActiveItemIDs()[0])
        return

    def start(self):
        super(HBSubdivisionItemController, self).start()
        self._gameEventController.onPrbEntityStateChanged += self.__onPrbEntitySwitched

    def stop(self):
        self._gameEventController.onPrbEntityStateChanged -= self.__onPrbEntitySwitched
        super(HBSubdivisionItemController, self).stop()

    def getInstanceClass(self):
        return HBSubdivisionItem

    def __onPrbEntitySwitched(self):
        self.setSelectedSubdivisionID(self.getActiveItemIDs()[0])

    def getSelectedSubdivisionID(self):
        return self.selectedSubdivisionID

    def setSelectedSubdivisionID(self, value):
        value = value
        isChanged = self.selectedSubdivisionID != value
        if isChanged:
            self.selectedSubdivisionID = value
            self.__cacheSelectedSubdivisionId()
        return isChanged

    def _getConfig(self):
        settings = self._gameEventController.getGameEventData()
        return settings

    def getSubdivisionsConfig(self):
        return self._getConfig().get('divisions', {})

    def getActiveItemIDs(self):
        conf = self.getSubdivisionsConfig()
        activeItems = [ key for key, value in conf.items() if value.get('frontID', None) == self.frontID ]
        return activeItems

    def __cacheSelectedSubdivisionId(self):
        self._gameEventController.frontController.setCachedSelectedSubdivisionId(self.frontID, self.selectedSubdivisionID)


class HBSubdivisionItem(GameEventCollection):
    itemsCache = dependency.descriptor(IItemsCache)
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, divisionID):
        super(HBSubdivisionItem, self).__init__()
        self._id = divisionID
        self.__exp = 0

    def init(self):
        super(HBSubdivisionItem, self).init()
        account = BigWorld.player()
        account.historicalBattles.onHBDataChanged += self.__onHBDataChanged

    def fini(self):
        account = BigWorld.player()
        account.historicalBattles.onHBDataChanged -= self.__onHBDataChanged
        super(HBSubdivisionItem, self).fini()

    @property
    def subdivisionLockCache(self):
        return BigWorld.player().HBAccountComponent.subdivisionLock or {}

    def getID(self):
        return self._id

    def isLocked(self):
        return self.getID() in self.subdivisionLockCache

    def _onSyncCompleted(self):
        self.__resyncExp()
        self.onItemsUpdated()

    def isInBattle(self):
        return False

    def _getSubdivisionData(self):
        return self.gameEventController.getGameEventData().get('divisions', {}).get(self.getID(), None)

    def _getTankSetsData(self):
        subdivision = self._getSubdivisionData()
        return subdivision.get('tankSets', [])

    def getAbilitiesData(self):
        subdivision = self._getSubdivisionData()
        return subdivision.get('abilities', [])

    def getTanksIntCDByProgressionLevel(self, vehicleProgressionLevel):
        tankSetsData = self._getTankSetsData()
        tankSet = tankSetsData[vehicleProgressionLevel]
        return tankSet

    def getEXP(self):
        return self.__exp

    def getProgressionLevel(self):
        exp = self.getEXP()
        config = self.gameEventController.getGameEventData()
        return getDivisionLevelByExp(config, self._id, exp)

    def getTanksIntCDForCurrentProgressionLevel(self):
        return self.getTanksIntCDByProgressionLevel(self.getProgressionLevel())

    def getTanksForCurrentProgressionLevel(self):
        currentLevel = self.getProgressionLevel()
        return [ self.itemsCache.items.getItemByCD(intCD) for intCD in self.getTanksIntCDByProgressionLevel(currentLevel) ]

    def getMaxExpForCurrentLevel(self):
        config = self.gameEventController.getGameEventData()
        return getDivisionCurrentLevelMaxExp(config, self.getID(), self.getEXP())

    def getVehiclesType(self):
        tanksSet = self.getTanksIntCDByProgressionLevel(self.getProgressionLevel())
        if not tanksSet:
            _logger.error('[HBSubdivisionItem] tanksSet is empty')
            return
        vehicleCD = tanksSet[0]
        vehType = vehicles.getItemByCompactDescr(vehicleCD)
        return vehType.classTag

    def __onHBDataChanged(self):
        self.__resyncExp(notify=True)
        self.onItemsUpdated()

    def __resyncExp(self, notify=False):
        prevExp = self.__exp
        subdivisionsEXP = self.itemsCache.items.historicalBattles.subdivisionsProgressEXP
        self.__exp = subdivisionsEXP.get(self.getID(), 0)
        if not notify or self.__exp == prevExp:
            return
        config = self.gameEventController.getGameEventData()
        prevLvl = getDivisionLevelByExp(config, self._id, prevExp)
        currLvl = getDivisionLevelByExp(config, self._id, self.__exp)
        if currLvl > prevLvl:
            self.gameEventController.onDivisionLevelUp(self._id, prevLvl, currLvl)
