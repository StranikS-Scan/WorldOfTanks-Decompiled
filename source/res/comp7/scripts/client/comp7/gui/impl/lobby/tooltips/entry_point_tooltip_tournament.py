# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/entry_point_tooltip_tournament.py
import typing
from comp7.gui.impl.gen.view_models.views.lobby.enums import TournamentName
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.tournament_entry_point_tooltip_model import TournamentEntryPointTooltipModel, TournamentState
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from helpers.ingame_tournament_helper import IngameTournamentState
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import IIngameTournamentController
if typing.TYPE_CHECKING:
    from helpers.ingame_tournament_helper import IngameTournamentType

class Comp7TournamentEntryPointTooltip(ViewImpl):
    __ingameTournamentController = dependency.descriptor(IIngameTournamentController)
    __tournamentStateTooltipStateMap = {IngameTournamentState.INTRO: TournamentState.STARTINGSOON,
     IngameTournamentState.IN_PROGRESS: TournamentState.LIVE,
     IngameTournamentState.BETWEEN_SHOWMATCHES: TournamentState.BETWEENSHOWMATCHES,
     IngameTournamentState.FINISHED: TournamentState.FINISHED}

    def __init__(self, tounamentType):
        self.__tournamentType = tounamentType
        settings = ViewSettings(R.views.comp7.mono.lobby.tooltips.tournament_entry_point_tooltip())
        settings.model = TournamentEntryPointTooltipModel()
        super(Comp7TournamentEntryPointTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(Comp7TournamentEntryPointTooltip, self).getViewModel()

    def _getEvents(self):
        return ((self.__ingameTournamentController.onTournamentEntryPointUpdated, self._updateState),)

    def _onLoading(self, *args, **kwargs):
        super(Comp7TournamentEntryPointTooltip, self)._onLoading(*args, **kwargs)
        self._updateState()

    def _onStatusUpdated(self, _):
        self._updateState()

    def _onStatusTick(self):
        self._updateState()

    def _updateState(self):
        tournamentState = self.__ingameTournamentController.getTournamentState(self.__tournamentType)
        startDate, endDate = self.__ingameTournamentController.getTournamentShowmatchPeriod(self.__tournamentType)
        formattedServerTimestamp = int(round(getServerUTCTime()))
        with self.viewModel.transaction() as tx:
            tx.setTournamentName(TournamentName(self.__tournamentType.value))
            tx.setStartTimestamp(startDate)
            tx.setEndTimestamp(endDate)
            tx.setState(self.__tournamentStateTooltipStateMap.get(tournamentState))
            currentShowmatch = self.__ingameTournamentController.getCurrentShowmatch(self.__tournamentType)
            if currentShowmatch:
                tx.setTimeLeftUntilLiveMatch(currentShowmatch.endTime - formattedServerTimestamp)
            nextMatch = self.__ingameTournamentController.getNextShowmatch(self.__tournamentType)
            if nextMatch:
                tx.setTimeLeftUntilNextShowMatchDay(nextMatch.startTime - formattedServerTimestamp)
