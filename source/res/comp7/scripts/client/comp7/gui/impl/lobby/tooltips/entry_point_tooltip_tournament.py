# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/entry_point_tooltip_tournament.py
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.tournament_entry_point_tooltip_model import TournamentEntryPointTooltipModel, TournamentState
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from helpers.ingame_tournament_helper import IngameTournamentState
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import IIngameTournamentController

class Comp7TournamentEntryPointTooltip(ViewImpl):
    __ingameTournamentController = dependency.descriptor(IIngameTournamentController)
    __tournamentStateTooltipStateMap = {IngameTournamentState.INTRO: TournamentState.STARTINGSOON,
     IngameTournamentState.IN_PROGRESS: TournamentState.LIVE,
     IngameTournamentState.BETWEEN_SHOWMATCHES: TournamentState.BETWEENSHOWMATCHES,
     IngameTournamentState.FINISHED: TournamentState.FINISHED}

    def __init__(self):
        settings = ViewSettings(R.views.comp7.mono.lobby.tooltips.tournament_entry_point_tooltip())
        settings.model = TournamentEntryPointTooltipModel()
        super(Comp7TournamentEntryPointTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(Comp7TournamentEntryPointTooltip, self).getViewModel()

    def _getEvents(self):
        return ((self.__ingameTournamentController.onTournamentBannerUpdated, self._updateState),)

    def _onLoading(self, *args, **kwargs):
        super(Comp7TournamentEntryPointTooltip, self)._onLoading(*args, **kwargs)
        self._updateState()

    def _onStatusUpdated(self, _):
        self._updateState()

    def _onStatusTick(self):
        self._updateState()

    def _updateState(self):
        bannerData = self.__ingameTournamentController.getActiveBannerData()
        if bannerData is None:
            return
        else:
            bannerState = bannerData.state
            tournamentStartDate, tournamentEndDate = self.__ingameTournamentController.getTournamentDates()
            formattedServerTimestamp = int(round(getServerUTCTime()))
            with self.viewModel.transaction() as tx:
                tx.setStartTimestamp(tournamentStartDate)
                tx.setEndTimestamp(tournamentEndDate)
                tx.setState(self.__tournamentStateTooltipStateMap.get(bannerState))
                tx.setTimeLeftUntilLiveMatch(bannerData.endTime - formattedServerTimestamp)
                tx.setTimeLeftUntilNextShowMatchDay(bannerData.endTime - formattedServerTimestamp)
            return
