# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_leagues.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.ranked_battles.ranked_builders import leagues_vos
from gui.ranked_battles.ranked_helpers.league_provider import UNDEFINED_LEAGUE_ID
from gui.ranked_battles import ranked_helpers
from helpers import dependency
from gui.Scaleform.daapi.view.meta.RankedBattlesLeaguesViewMeta import RankedBattlesLeaguesViewMeta
from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_page import IResetablePage
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.shared import IItemsCache

class RankedBattlesLeaguesView(RankedBattlesLeaguesViewMeta, IResetablePage):
    rankedController = dependency.descriptor(IRankedBattlesController)
    itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    def reset(self):
        pass

    def _populate(self):
        super(RankedBattlesLeaguesView, self)._populate()
        g_clientUpdateManager.addCallbacks({'stats.dossier': self.__dossierUpdateCallBack})
        self.rankedController.onUpdated += self.__onRankedUpdate
        self.rankedController.getLeagueProvider().onLeagueUpdated += self.__onLeagueUpdate
        self.__setEfficiencyData()
        self.__setStatsData()
        self.__setBonusBattlesCount()
        self.__setEmptyLeagueAndPositionData()
        self.rankedController.getLeagueProvider().forceUpdateLeague()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.rankedController.onUpdated -= self.__onRankedUpdate
        self.rankedController.getLeagueProvider().onLeagueUpdated -= self.__onLeagueUpdate
        super(RankedBattlesLeaguesView, self)._dispose()

    def __dossierUpdateCallBack(self, *args):
        self.__setStatsData()
        self.__setEfficiencyData()

    def __onLeagueUpdate(self):
        self.__setLeagueAndPositionData()

    def __onRankedUpdate(self):
        self.__setStatsData()
        self.__setEfficiencyData()
        self.__setBonusBattlesCount()

    def __setBonusBattlesCount(self):
        bonusBattlesCount = self.rankedController.getStatsComposer().bonusBattlesCount
        self.as_setBonusBattlesLabelS(ranked_helpers.getBonusBattlesLabel(bonusBattlesCount))

    def __setEfficiencyData(self):
        statsComposer = self.rankedController.getStatsComposer()
        currentSeasonEfficiency = statsComposer.currentSeasonEfficiency.efficiency
        currentSeasonEfficiencyDiff = statsComposer.currentSeasonEfficiencyDiff
        self.as_setEfficiencyDataS(leagues_vos.getEfficiencyVO(currentSeasonEfficiency, currentSeasonEfficiencyDiff))

    def __setEmptyLeagueAndPositionData(self):
        self.as_setDataS(leagues_vos.getLeagueVO(UNDEFINED_LEAGUE_ID))
        self.as_setRatingDataS(leagues_vos.getRatingVO(None))
        return

    def __setLeagueAndPositionData(self):
        webLeague = self.rankedController.getLeagueProvider().webLeague
        if webLeague.league == UNDEFINED_LEAGUE_ID:
            webLeague = self.rankedController.getClientLeague()
        if webLeague.league != UNDEFINED_LEAGUE_ID and webLeague.position is not None:
            league = webLeague.league
            position = webLeague.position
            self.as_setDataS(leagues_vos.getLeagueVO(league))
            self.as_setRatingDataS(leagues_vos.getRatingVO(position))
        return

    def __setStatsData(self):
        statsComposer = self.rankedController.getStatsComposer()
        self.as_setStatsDataS(leagues_vos.getStatsVO(statsComposer.amountStepsInLeagues, statsComposer.amountBattlesInLeagues, statsComposer.amountSteps, statsComposer.amountBattles))
