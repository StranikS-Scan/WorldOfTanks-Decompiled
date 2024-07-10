# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/tournament_banner_view.py
import logging
from urlparse import urljoin
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle_royale.tournament_banner_base_view_model import TournamentState
from gui.impl.gen.view_models.views.battle_royale.tournament_banner_view_model import TournamentBannerViewModel
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, events
from gui.tournament.tournament_helpers import isTournamentEnabled, showTournaments, getIgbHost
from helpers import dependency, time_utils
from skeletons.gui.game_control import IBattleRoyaleController
from battle_royale.gui.impl.lobby.tooltips.tournament_banner_tooltip_view import TournamentBannerTooltipView
from gui.shared.utils.graphics import isRendererPipelineDeferred
_logger = logging.getLogger(__name__)
CHALLENGE_TAB_ROUTE = '/challenges'
OPEN_TOURNAMENTS_URL = 'openTournamentChallenge'
WIDGET_TO_TOURNAMENT_STATE = {'beforeTournament': TournamentState.BEFORETOURNAMENT,
 'activeTournament': TournamentState.ACTIVETOURNAMENT,
 'afterTournament': TournamentState.AFTERTOURNAMENT,
 'announcementStream': TournamentState.ANNOUNCEMENTSTREAM,
 'activeStream': TournamentState.ACTIVESTREAM}

def getTimestampDelta(timestamp):
    return timestamp - time_utils.getCurrentLocalServerTimestamp()


class TournamentBannerView(ViewImpl):
    __slots__ = ('__bannerData', '__isExtended')
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, isExtended=False, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.battle_royale.lobby.views.TournamentBannerView())
        settings.flags = flags
        settings.model = TournamentBannerViewModel()
        self.__bannerData = {}
        self.__isExtended = isExtended
        super(TournamentBannerView, self).__init__(settings)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.battle_royale.lobby.tooltips.TournamentBannerTooltipView():
            if self.__bannerData:
                return TournamentBannerTooltipView(WIDGET_TO_TOURNAMENT_STATE[self.__bannerData['state']], self.__bannerData['startDate'], self.__bannerData['endDate'])
        return super(TournamentBannerView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return super(TournamentBannerView, self).getViewModel()

    def setIsExtended(self, value):
        self.__isExtended = value
        self.__updateState()

    def _getEvents(self):
        return ((self.__battleRoyaleController.onTournamentBannerStateChanged, self.__updateState), (self.viewModel.onClick, self.__onClick))

    def _onLoading(self, *args, **kwargs):
        super(TournamentBannerView, self)._onLoading(*args, **kwargs)
        self.__updateState()

    def __onClick(self):
        if self.__bannerData and self.__bannerData.has_key('url'):
            url = self.__bannerData['url']
            if url == OPEN_TOURNAMENTS_URL:
                self.__openTournaments()
            else:
                g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.SPECIFIED, url))

    @staticmethod
    def __openTournaments():
        if isTournamentEnabled():
            showTournaments(url=urljoin(getIgbHost(), CHALLENGE_TAB_ROUTE))
        else:
            _logger.warning('Trying to open tournaments when isTournamentEnabled = False')

    def __updateState(self):
        if not isTournamentEnabled():
            return
        with self.viewModel.transaction() as tx:
            self.__bannerData = self.__battleRoyaleController.getTournamentBannerData()
            if not self.__bannerData:
                logging.warning('No widget data to show')
                return
            tournamentState = WIDGET_TO_TOURNAMENT_STATE.get(self.__bannerData['state'])
            if not tournamentState:
                logging.warning('Incorrect widget state=%s', self.__bannerData['state'])
                return
            tx.setState(tournamentState)
            tx.setDateEnd(getTimestampDelta(self.__bannerData['endDate']))
            tx.setDateStart(getTimestampDelta(self.__bannerData['startDate']))
            tx.setIsExtended(self.__isExtended)
            tx.setImprovedGraphics(isRendererPipelineDeferred())
