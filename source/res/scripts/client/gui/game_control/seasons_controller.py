# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/seasons_controller.py
from constants import GameSeasonType
from soft_exception import SoftException
from helpers import dependency
from skeletons.gui.game_control import ISeasonsController, IRankedBattlesController, IEpicBattleMetaGameController, IBattleRoyaleController, IMapboxController, IEventBattlesController, IComp7Controller
from skeletons.gui.game_control import ISeasonProvider

class SeasonsController(ISeasonsController):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __epicMetaController = dependency.descriptor(IEpicBattleMetaGameController)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __mapboxController = dependency.descriptor(IMapboxController)
    __eventBattlesController = dependency.descriptor(IEventBattlesController)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self):
        super(SeasonsController, self).__init__()
        self.__seasonProvidersByType = {}

    @property
    def _seasonProvidersByType(self):
        if not self.__seasonProvidersByType:
            self.__seasonProvidersByType = {GameSeasonType.RANKED: self.__rankedController,
             GameSeasonType.EPIC: self.__epicMetaController,
             GameSeasonType.BATTLE_ROYALE: self.__battleRoyaleController,
             GameSeasonType.MAPBOX: self.__mapboxController,
             GameSeasonType.EVENT_BATTLES: self.__eventBattlesController,
             GameSeasonType.COMP7: self.__comp7Controller}
        return self.__seasonProvidersByType

    def hasAnySeason(self, seasonType):
        return self.__getSeasonProviderChecked(seasonType).hasAnySeason()

    def getCurrentSeason(self, seasonType):
        return self.__getSeasonProviderChecked(seasonType).getCurrentSeason()

    def getCurrentCycleID(self, seasonType):
        return self.__getSeasonProviderChecked(seasonType).getCurrentCycleID()

    def getSeason(self, seasonType, seasonID):
        return self.__getSeasonProviderChecked(seasonType).getSeason(seasonID)

    def isSeasonActive(self, seasonID, seasonType):
        season = self.getCurrentSeason(seasonType)
        return season is not None and season.getSeasonID() == seasonID

    def isWithinSeasonTime(self, seasonID, seasonType):
        return self.__getSeasonProviderChecked(seasonType).isWithinSeasonTime(seasonID)

    def isSeasonCycleActive(self, cycleID, seasonType):
        return self.getCurrentCycleID(seasonType) == cycleID

    def __getSeasonProviderChecked(self, seasonType):
        controllerToUse = self._seasonProvidersByType.get(seasonType, None)
        if controllerToUse is None:
            raise SoftException('Invalid seasonType [{}]! No suitable season provider found.'.format(seasonType))
        return controllerToUse
