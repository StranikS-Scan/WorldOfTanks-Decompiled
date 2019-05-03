# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_season_gap.py
import time
from helpers import dependency, time_utils
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.ranked_battles.ranked_builders import season_gap_vos
from gui.ranked_battles.ranked_helpers.league_provider import UNDEFINED_LEAGUE_ID
from gui.ranked_battles.constants import SeasonResultTokenPatterns, RankedDossierKeys, ZERO_RANK_ID, SeasonGapStates, NOT_IN_LEAGUES_QUEST
from gui.Scaleform.daapi.view.meta.RankedBattlesSeasonGapViewMeta import RankedBattlesSeasonGapViewMeta
from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_page import IResetablePage
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
_STATE_TO_READY_GAP_STATE = {SeasonGapStates.WAITING_IN_DIVISIONS: SeasonGapStates.IN_DIVISIONS,
 SeasonGapStates.WAITING_NOT_IN_SEASON: SeasonGapStates.NOT_IN_SEASON}
_STATE_TO_BANNED_GAP_STATE = {SeasonGapStates.WAITING_IN_LEAGUES: SeasonGapStates.BANNED_IN_LEAGUES,
 SeasonGapStates.WAITING_IN_DIVISIONS: SeasonGapStates.BANNED_IN_DIVISIONS,
 SeasonGapStates.WAITING_NOT_IN_SEASON: SeasonGapStates.BANNED_NOT_IN_SEASON,
 SeasonGapStates.IN_LEAGUES: SeasonGapStates.BANNED_IN_LEAGUES,
 SeasonGapStates.IN_DIVISIONS: SeasonGapStates.BANNED_IN_DIVISIONS,
 SeasonGapStates.NOT_IN_SEASON: SeasonGapStates.BANNED_NOT_IN_SEASON}

class RankedBattlesSeasonGapView(RankedBattlesSeasonGapViewMeta, IResetablePage):
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __TOKENS_ORDER = (SeasonResultTokenPatterns.RANKED_OFF_BANNED,
     SeasonResultTokenPatterns.RANKED_OFF_BRONZE_LEAGUE_TOKEN,
     SeasonResultTokenPatterns.RANKED_OFF_SILVER_LEAGUE_TOKEN,
     SeasonResultTokenPatterns.RANKED_OFF_GOLD_LEAGUE_TOKEN)
    __slots__ = ()

    def __init__(self):
        super(RankedBattlesSeasonGapView, self).__init__()
        self.__periodicNotifier = None
        self.__prevSeason = None
        self.__dossier = None
        self.__resultState = None
        self.__resultLeague = UNDEFINED_LEAGUE_ID
        return

    def reset(self):
        self.__update()

    def onBtnClick(self):
        self.__rankedController.showRankedBattlePage(ctx={'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RATING_ID})

    def _populate(self):
        super(RankedBattlesSeasonGapView, self)._populate()
        self.__rankedController.onUpdated += self.__update
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__prevSeason = self.__rankedController.getPreviousSeason()
        self.__dossier = self.__itemsCache.items.getAccountDossier().getSeasonRankedStats(RankedDossierKeys.SEASON % self.__prevSeason.getNumber(), self.__prevSeason.getSeasonID())
        self.__periodicNotifier = PeriodicNotifier(self.__getTillUpdateTime, self.__update)
        self.__update()
        self.__periodicNotifier.startNotification()

    def _dispose(self):
        self.__rankedController.onUpdated -= self.__update
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__periodicNotifier.stopNotification()
        self.__periodicNotifier.clear()
        super(RankedBattlesSeasonGapView, self)._dispose()

    def __getResultTokenPattern(self):
        prevSeasonID = self.__prevSeason.getSeasonID()
        for tokenPattern in self.__TOKENS_ORDER:
            tokenName = tokenPattern.format(prevSeasonID)
            token = self.__itemsCache.items.tokens.getTokens().get(tokenName)
            if token:
                _, count = token
                if count > 0:
                    return tokenPattern

        return None

    def __getNotLeagueQuest(self):
        return self.__eventsCache.getHiddenQuests().get(NOT_IN_LEAGUES_QUEST.format(self.__prevSeason.getSeasonID()))

    def __getTillUpdateTime(self):
        notLeagueQuest = self.__getNotLeagueQuest()
        return notLeagueQuest.getStartTimeLeft() if notLeagueQuest is not None else time_utils.ONE_MINUTE

    def __onTokensUpdate(self, _):
        self.__update()

    def __update(self):
        self.__updateStateByDossier()
        self.__updateStateByTokens()
        self.__updateEfficiency()
        self.__updateRating()
        self.__updateData()

    def __updateData(self):
        achievedRankID = self.__dossier.getAchievedRank()
        achievedDivision = self.__rankedController.getDivision(achievedRankID)
        self.as_setDataS(season_gap_vos.getDataVO(self.__resultState, achievedRankID, achievedDivision, self.__resultLeague))

    def __updateEfficiency(self):
        self.as_setEfficiencyDataS(season_gap_vos.getEfficiencyVO(self.__dossier.getStepsEfficiency()))

    def __updateRating(self):
        isMastered = self.__resultState in (SeasonGapStates.IN_LEAGUES, SeasonGapStates.WAITING_IN_LEAGUES)
        webLeague = self.__rankedController.getLeagueProvider().webLeague
        if webLeague.league != self.__resultLeague:
            webLeague = self.__rankedController.getClientLeague()
        position = webLeague.position if webLeague.league == self.__resultLeague else None
        self.as_setRatingDataS(season_gap_vos.getRatingVO(position, isMastered))
        return

    def __updateStateByDossier(self):
        achievedRank = self.__dossier.getAchievedRank()
        self.__resultState = SeasonGapStates.WAITING_IN_LEAGUES
        if achievedRank == ZERO_RANK_ID:
            self.__resultState = SeasonGapStates.WAITING_NOT_IN_SEASON
        elif achievedRank < self.__rankedController.getMaxPossibleRank():
            self.__resultState = SeasonGapStates.WAITING_IN_DIVISIONS

    def __updateStateByTokens(self):
        self.__resultLeague = UNDEFINED_LEAGUE_ID
        resultTokenPattern = self.__getResultTokenPattern()
        if resultTokenPattern == SeasonResultTokenPatterns.RANKED_OFF_BANNED:
            self.__resultState = _STATE_TO_BANNED_GAP_STATE.get(self.__resultState, self.__resultState)
        elif resultTokenPattern is not None:
            self.__resultState = SeasonGapStates.IN_LEAGUES
            self.__resultLeague = int(resultTokenPattern.split('_')[-1])
        else:
            notLeagueQuest = self.__getNotLeagueQuest()
            if notLeagueQuest is not None and notLeagueQuest.getStartTime() < time.time():
                self.__resultState = _STATE_TO_READY_GAP_STATE.get(self.__resultState, self.__resultState)
        return
