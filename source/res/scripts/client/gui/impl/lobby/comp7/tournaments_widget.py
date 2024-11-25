# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/tournaments_widget.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.meta.EventTournamentBannerInjectMeta import EventTournamentBannerInjectMeta
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.tournaments_widget_model import TournamentsWidgetModel, TournamentsState
from gui.impl.pub import ViewImpl
from gui.tournament.tournament_helpers import isTournamentEnabled, showTournaments
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
_logger = logging.getLogger(__name__)
WIDGET_TO_TOURNAMENT_STATE = {'active': TournamentsState.ACTIVE,
 'registration': TournamentsState.REGISTRATION}

class TournamentsWidgetComponent(EventTournamentBannerInjectMeta):
    __slots__ = ('__view',)

    def __init__(self):
        super(TournamentsWidgetComponent, self).__init__()
        self.__view = None
        return

    def setIsExtended(self, value):
        if self.__view is not None:
            self.__view.setIsExtended(value)
        return

    def _dispose(self):
        self.__view = None
        super(TournamentsWidgetComponent, self)._dispose()
        return

    def _makeInjectView(self):
        self.__view = TournamentsWidget(flags=ViewFlags.VIEW)
        return self.__view


class TournamentsWidget(ViewImpl):
    __slots__ = ()
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.comp7.TournamentsWidget())
        settings.flags = flags
        settings.model = TournamentsWidgetModel()
        super(TournamentsWidget, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TournamentsWidget, self).getViewModel()

    def setIsExtended(self, value):
        with self.viewModel.transaction() as tx:
            tx.setIsExtended(value)

    def _initialize(self, *args, **kwargs):
        super(TournamentsWidget, self)._initialize(*args, **kwargs)
        self.viewModel.onOpenTournaments += self.__onOpenTournaments

    def _finalize(self):
        self.viewModel.onOpenTournaments -= self.__onOpenTournaments
        super(TournamentsWidget, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(TournamentsWidget, self)._onLoading(*args, **kwargs)
        comp7Settings = self.__comp7Controller.getModeSettings()
        if isTournamentEnabled() and comp7Settings.tournaments.get('isBannerEnabled', False):
            self.__updateState()

    def __onOpenTournaments(self):
        if isTournamentEnabled():
            showTournaments()
        else:
            _logger.warning('Trying to open tournaments when isTournamentEnabled = False')

    def __updateState(self):
        with self.viewModel.transaction() as tx:
            widgetData = self.__comp7Controller.getTournamentBannerData()
            if not widgetData:
                logging.warning('No widget data to show')
                return
            tournamentState = WIDGET_TO_TOURNAMENT_STATE.get(widgetData['state'])
            if not tournamentState:
                logging.warning('Incorrect widget state=%s', widgetData['state'])
                return
            tx.setIsEnabled(True)
            tx.setState(tournamentState)
