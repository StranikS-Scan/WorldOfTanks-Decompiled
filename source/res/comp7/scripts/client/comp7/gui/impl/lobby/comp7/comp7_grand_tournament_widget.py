# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/comp7/comp7_grand_tournament_widget.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.CarouselBannerInjectMeta import CarouselBannerInjectMeta
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.comp7_grand_tournament_widget_model import Comp7GrandTournamentWidgetModel, Comp7GrandTournamentState
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
_logger = logging.getLogger(__name__)
WIDGET_TO_TOURNAMENT_STATE = {'countdown': Comp7GrandTournamentState.COUNTDOWN,
 'live': Comp7GrandTournamentState.LIVE,
 'dayIsOver': Comp7GrandTournamentState.DAYISOVER,
 'finished': Comp7GrandTournamentState.FINISHED}

class Comp7GrandTournamentsWidgetComponent(CarouselBannerInjectMeta):
    __slots__ = ('__view',)

    def __init__(self):
        super(Comp7GrandTournamentsWidgetComponent, self).__init__()
        self.__view = None
        return

    def setIsExtended(self, value):
        if self.__view is not None:
            self.__view.setIsExtended(value)
        return

    def _dispose(self):
        self.__view = None
        super(Comp7GrandTournamentsWidgetComponent, self)._dispose()
        return

    def _makeInjectView(self):
        self.__view = Comp7GrandTournamentWidget(flags=ViewFlags.VIEW)
        return self.__view


class Comp7GrandTournamentWidget(ViewImpl):
    __slots__ = ('__state',)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.comp7.GrandTournamentWidget())
        settings.flags = flags
        settings.model = Comp7GrandTournamentWidgetModel()
        self.__state = None
        super(Comp7GrandTournamentWidget, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(Comp7GrandTournamentWidget, self).getViewModel()

    def setIsExtended(self, value):
        with self.viewModel.transaction() as tx:
            tx.setIsExtended(value)

    def _initialize(self, *args, **kwargs):
        super(Comp7GrandTournamentWidget, self)._initialize(*args, **kwargs)
        self.viewModel.onOpenComp7GrandTournament += self.__onOpenComp7GrandTournament
        self.__comp7Controller.onGrandTournamentBannerUpdate += self.__updateBanner

    def _finalize(self):
        self.viewModel.onOpenComp7GrandTournament -= self.__onOpenComp7GrandTournament
        self.__comp7Controller.onGrandTournamentBannerUpdate -= self.__updateBanner
        super(Comp7GrandTournamentWidget, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(Comp7GrandTournamentWidget, self)._onLoading(*args, **kwargs)
        self.__updateBanner()

    def __onOpenComp7GrandTournament(self):
        urlDict = GUI_SETTINGS.lookup('comp7GrandTournamentBanner')
        if urlDict is None:
            return
        else:
            url = urlDict[self.__state]
            showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))
            return

    def __updateBanner(self):
        with self.viewModel.transaction() as tx:
            widgetData = self.__comp7Controller.getGrandTournamentBannerData()
            self.__state = widgetData['state']
            if not widgetData:
                logging.warning('No widget data to show')
                return
            tournamentState = WIDGET_TO_TOURNAMENT_STATE.get(self.__state)
            if not tournamentState:
                logging.warning('Incorrect widget state=%s', self.__state)
                return
            tx.setState(tournamentState)
            timeLeft = widgetData['timeLeft']
            tx.setTimeLeft(timeLeft)
