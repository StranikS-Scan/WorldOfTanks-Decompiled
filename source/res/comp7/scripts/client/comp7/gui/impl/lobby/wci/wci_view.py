# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/wci/wci_view.py
import logging
import random
import typing
from comp7.gui.impl.gen.view_models.views.lobby.wci.match_model import MatchModel, MatchState, MatchStage
from comp7.gui.impl.gen.view_models.views.lobby.wci.team_model import TeamModel
from comp7.gui.impl.gen.view_models.views.lobby.wci.wci_view_model import WciViewModel, OverviewState, Streaming, PageState
from frameworks.wulf import ViewSettings, ViewFlags, WindowFlags
from frameworks.wulf.view.array import fillViewModelsArray
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.ingame_tournament_helper import IngameTournamentMatchState, IngameTournamentUrlType, IngameTournamentLogoSize, IngameTournamentBracketType
from helpers.time_utils import ONE_MINUTE, getServerUTCTime
from skeletons.gui.game_control import IExternalLinksController, IIngameTournamentController
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from gui.game_control.ingame_tournament_controller import _MatchData, _TeamData, _LeaderboardData, _RewardData

class WCIView(ViewImpl):
    __tournamentCtrl = dependency.descriptor(IIngameTournamentController)
    __externalLinksCtrl = dependency.descriptor(IExternalLinksController)
    _INGAME_TOURNAMENT_MATCH_STATE_TO_UI_STATE = {IngameTournamentMatchState.UPCOMING: MatchState.NOTSTARTED,
     IngameTournamentMatchState.IN_LIVE: MatchState.LIVE,
     IngameTournamentMatchState.COMPLETED: MatchState.COMPLETED}
    _TIMER_UPDATE_RANDOM_DELTA = ONE_MINUTE
    _BRACKET_TYPE_TO_MATCH_STAGE = {IngameTournamentBracketType.RR: MatchStage.ROUNDROBIN}
    _MATCH_ROUND_TO_MATCH_STAGE = {3: MatchStage.ROUNDROBIN,
     2: MatchStage.UBSEMIFINALS,
     1: MatchStage.UBFINALS,
     0: MatchStage.GRANDFINALS,
     -4: MatchStage.LBROUND1,
     -3: MatchStage.LBROUND2,
     -2: MatchStage.LBSEMIFINALS,
     -1: MatchStage.LBFINALS}

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.comp7.mono.lobby.wci())
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = WciViewModel()
        super(WCIView, self).__init__(settings)
        self.__callbackDelayer = CallbackDelayer()
        self.__data = None
        return

    @property
    def viewModel(self):
        return super(WCIView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onWatchStreamingOne, self.__onWatchStreamOne),
         (self.viewModel.onWatchStreamingTwo, self.__onWatchStreamTwo),
         (self.viewModel.onGoToShop, self.__onGoToShop),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.onRefresh, self.__onRefresh))

    def _onLoading(self, *args, **kwargs):
        super(WCIView, self)._onLoading(*args, **kwargs)
        self.viewModel.setPageState(PageState.LOADING)
        self.__tournamentCtrl.onTournamentWGCGDataUpdated += self.__onTournamentWGCGDataUpdated
        self.__updateTournamentData()

    def _finalize(self):
        super(WCIView, self)._finalize()
        self.__callbackDelayer.destroy()
        self.__callbackDelayer = None
        self.__tournamentCtrl.onTournamentWGCGDataUpdated -= self.__onTournamentWGCGDataUpdated
        self.__data = None
        return

    def __updateTournamentData(self):
        self.viewModel.setIsRefreshing(True)
        self.__tournamentCtrl.requestTournamentWGCGData()

    def __onTournamentWGCGDataUpdated(self, data):
        self.__data = data
        self.__fillModelData()

    def __fillModelData(self):
        with self.viewModel.transaction() as vm:
            vm.setPageState(PageState.CONTENT)
            vm.setOverviewState(self.__getOverviewState())
            vm.setIsRefreshing(False)
            if self.__data is not None:
                vm.setPrizeFund(self.__data.getTotalRewardAmount())
                matches = []
                for matchData in self.__data.getAllMatches():
                    matchModel = MatchModel()
                    self.__fillMatchData(matchModel, matchData)
                    matches.append(matchModel)

                fillViewModelsArray(matches, vm.getSchedule())
                teams = []
                for leaderboardData in self.__data.leaderboard:
                    for teamID in leaderboardData.teamIDs:
                        teamModel = TeamModel()
                        self.__fillTeamData(teamModel, teamID)
                        teams.append(teamModel)

                fillViewModelsArray(teams, vm.getFundDistribution())
                self.__fillStreamingTypes()
        self.__setUpdateCallback()
        return

    def __getOverviewState(self):
        if self.__data is None:
            return OverviewState.ERROR
        elif self.__data.getLiveMatch() is not None:
            return OverviewState.LIVE
        else:
            return OverviewState.SCHEDULE if self.__data.getUpcomingMatches() else OverviewState.FINALRESULT

    def __fillStreamingTypes(self):
        with self.viewModel.transaction() as vm:
            if IngameTournamentUrlType.TWITCH in self.__data.streamURLs:
                vm.setStreamingWithDrops(Streaming.TWITCH)
            elif IngameTournamentUrlType.HUYA in self.__data.streamURLs:
                vm.setStreamingWithDrops(Streaming.HUYA)
            if IngameTournamentUrlType.YOUTUBE in self.__data.streamURLs:
                vm.setStreamingWithoutDrops(Streaming.YOUTUBE)
            elif IngameTournamentUrlType.DOUYIN in self.__data.streamURLs:
                vm.setStreamingWithoutDrops(Streaming.DOUYIN)

    def __fillMatchData(self, matchModel, matchData):
        matchModel.setStartOfMatchTimestamp(matchData.startTime)
        matchModel.setBestOf(matchData.bestOf)
        matchModel.setMatchState(self._INGAME_TOURNAMENT_MATCH_STATE_TO_UI_STATE[matchData.state])
        matchStage = self._BRACKET_TYPE_TO_MATCH_STAGE.get(matchData.bracketType, self._MATCH_ROUND_TO_MATCH_STAGE[matchData.round])
        matchModel.setMatchStage(matchStage)
        self.__fillTeamData(matchModel.team1, matchData.teamID1, matchData.state, matchData.teamScore1)
        self.__fillTeamData(matchModel.team2, matchData.teamID2, matchData.state, matchData.teamScore2)

    def __fillTeamData(self, teamModel, teamID, matchState=None, teamMatchScore=0):
        if teamID is None:
            return
        else:
            teamData = self.__data.teams.get(teamID)
            if teamData is not None:
                teamModel.setTeamName(teamData.name)
                logoUrls = teamData.logoURLs
                teamModel.logos.setX48(logoUrls.get(IngameTournamentLogoSize.SMALL, ''))
                teamModel.logos.setX86(logoUrls.get(IngameTournamentLogoSize.MEDIUM, ''))
                teamModel.logos.setX260(logoUrls.get(IngameTournamentLogoSize.LARGE, ''))
                teamModel.logos.setX522(logoUrls.get(IngameTournamentLogoSize.EXTRA_LARGE, ''))
                if matchState == IngameTournamentMatchState.COMPLETED:
                    teamModel.setScore(teamMatchScore)
                leaderboardData = self.__data.getLeaderboardDataByTeam(teamID)
                if leaderboardData is not None:
                    teamModel.setSharedPositionFrom(leaderboardData.fromPosition)
                    teamModel.setSharedPositionTo(leaderboardData.toPosition)
                    prize = self.__data.getRewardForPosition(leaderboardData.fromPosition)
                    if prize is not None:
                        teamModel.setPrize(prize.amount)
                    else:
                        teamModel.setPrize(0)
            else:
                _logger.warning('Team with ID %s not found in in teams', teamID)
            return

    def __setUpdateCallback(self):
        self.__callbackDelayer.clearCallbacks()
        if self.__data is not None:
            timers = []
            for match in self.__data.getUpcomingMatches():
                timers.append(match.startTime)

            if timers:
                timeTillUpdate = min(timers) - getServerUTCTime()
                delta = random.random() * self._TIMER_UPDATE_RANDOM_DELTA
                self.__callbackDelayer.delayCallback(timeTillUpdate + delta, self.__fillModelData)
        return

    def __onWatchStreamOne(self):
        if self.__data:
            url = self.__data.streamURLs.get(IngameTournamentUrlType.TWITCH) or self.__data.streamURLs.get(IngameTournamentUrlType.HUYA)
            if url:
                self.__externalLinksCtrl.open(url)
            else:
                _logger.warning('Could not open translation link one, url is not set')
        else:
            _logger.warning('Could not open translation link one, data is not set')

    def __onWatchStreamTwo(self):
        if self.__data:
            url = self.__data.streamURLs.get(IngameTournamentUrlType.YOUTUBE) or self.__data.streamURLs.get(IngameTournamentUrlType.DOUYIN)
            if url:
                self.__externalLinksCtrl.open(url)
            else:
                _logger.warning('Could not open translation link two, url is not set')
        else:
            _logger.warning('Could not open translation link two, data is not set')

    def __onGoToShop(self):
        self.__tournamentCtrl.openShop()

    def __onClose(self):
        showHangar()

    def __onRefresh(self):
        self.__updateTournamentData()


class WCIViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(WCIViewWindow, self).__init__(content=WCIView(), wndFlags=WindowFlags.WINDOW, decorator=None, parent=parent)
        return
