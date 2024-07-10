# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/seasons_controller.py
from constants import GameSeasonType
from soft_exception import SoftException
from helpers import dependency
from skeletons.gui.game_control import ISeasonsController, IRankedBattlesController, IEpicBattleMetaGameController, IMapboxController, IEventBattlesController, IComp7Controller
from gui.shared.system_factory import registerSeasonProviderHandler, collectSeasonProviderHandler
registerSeasonProviderHandler(GameSeasonType.RANKED, lambda *args, **kwargs: dependency.instance(IRankedBattlesController))
registerSeasonProviderHandler(GameSeasonType.EPIC, lambda *args, **kwargs: dependency.instance(IEpicBattleMetaGameController))
registerSeasonProviderHandler(GameSeasonType.MAPBOX, lambda *args, **kwargs: dependency.instance(IMapboxController))
registerSeasonProviderHandler(GameSeasonType.EVENT_BATTLES, lambda *args, **kwargs: dependency.instance(IEventBattlesController))
registerSeasonProviderHandler(GameSeasonType.COMP7, lambda *args, **kwargs: dependency.instance(IComp7Controller))

class SeasonsController(ISeasonsController):

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
        handler = collectSeasonProviderHandler(seasonType)
        if handler is None:
            raise SoftException('Invalid seasonType [{}]! No suitable season provider found.'.format(seasonType))
        return handler()
