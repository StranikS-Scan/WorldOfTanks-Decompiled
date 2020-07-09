# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_leagues.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.ranked_battles.ranked_builders import leagues_vos
from gui.ranked_battles.ranked_helpers.web_season_provider import UNDEFINED_LEAGUE_ID
from gui.ranked_battles import ranked_helpers
from helpers import dependency
from gui.Scaleform.daapi.view.meta.RankedBattlesLeaguesViewMeta import RankedBattlesLeaguesViewMeta
from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_page import IResetablePage
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.shared import IItemsCache

class RankedBattlesLeaguesView(RankedBattlesLeaguesViewMeta, IResetablePage):
    rankedController = dependency.descriptor(IRankedBattlesController)
    itemsCache = dependency.descriptor(IItemsCache)

    def reset(self):
        pass

    def _populate(self):
        super(RankedBattlesLeaguesView, self)._populate()
        g_clientUpdateManager.addCallbacks({'stats.dossier': self.__dossierUpdateCallBack})
        self.rankedController.onUpdated += self.__onRankedUpdate
        self.rankedController.getWebSeasonProvider().onInfoUpdated += self.__onWebSeasonInfoUpdate
        self.__setEfficiencyData()
        self.__setStatsData()
        self.__setBonusBattlesCount()
        self.__setEmptyLeagueAndPositionData()
        self.__setLeagueAndPositionData()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.rankedController.onUpdated -= self.__onRankedUpdate
        self.rankedController.getWebSeasonProvider().onInfoUpdated -= self.__onWebSeasonInfoUpdate
        super(RankedBattlesLeaguesView, self)._dispose()

    def __dossierUpdateCallBack(self, *_):
        self.__setStatsData()
        self.__setEfficiencyData()

    def __onWebSeasonInfoUpdate(self):
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
        self.as_setDataS(leagues_vos.getLeagueVO(UNDEFINED_LEAGUE_ID, False, False, 0))
        self.as_setRatingDataS(leagues_vos.getRatingVO(None))
        return

    def __setLeagueAndPositionData(self):
        webInfo = self.rankedController.getWebSeasonProvider().seasonInfo
        if webInfo.league == UNDEFINED_LEAGUE_ID:
            webInfo = self.rankedController.getClientSeasonInfo()
        if webInfo.league != UNDEFINED_LEAGUE_ID and webInfo.position is not None:
            self.as_setDataS(leagues_vos.getLeagueVO(webInfo.league, webInfo.isSprinter, webInfo.isTop, self.rankedController.getYearLBSize()))
            self.as_setRatingDataS(leagues_vos.getRatingVO(webInfo.position))
        return

    def __setStatsData(self):
        statsComposer = self.rankedController.getStatsComposer()
        self.as_setStatsDataS(leagues_vos.getStatsVO(statsComposer.amountStepsInLeagues, statsComposer.amountBattlesInLeagues, statsComposer.amountSteps, statsComposer.amountBattles))
