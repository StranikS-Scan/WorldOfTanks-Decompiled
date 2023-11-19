# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/battle_session_view.py
import typing
from adisp import adisp_process
from constants import TOURNAMENT_CONFIG
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.battle_session_model import BattleSessionModel
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.clans.clan_cache import g_clanCache
from gui.shared.view_helpers.emblems import getClanEmblemURL, EmblemSize
from gui.tournament.tournament_helpers import isTournamentEnabled, showTournaments
from helpers import dependency
from skeletons.gui.game_control import IExternalLinksController
from skeletons.gui.lobby_context import ILobbyContext
_TOURNAMENTS_URL = 'tournamentsURL'
_GLOBAL_MAP_URL = 'globalMapURL'

class BattleSessionView(ViewImpl):
    __slots__ = ()
    layoutID = R.views.lobby.mode_selector.BattleSessionView()
    __externalLinks = dependency.descriptor(IExternalLinksController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, layoutID):
        super(BattleSessionView, self).__init__(ViewSettings(layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, BattleSessionModel()))

    @property
    def viewModel(self):
        return super(BattleSessionView, self).getViewModel()

    def _getEvents(self):
        return ((self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),
         (self.viewModel.onClanClicked, self.__clanClickedHandler),
         (self.viewModel.onTournamentsClicked, self.__tournamentsClickedHandler),
         (self.viewModel.onGlobalMapClicked, self.__globalMapClickedHandler),
         (self.viewModel.onCloseClicked, self.__closeClickedHandler))

    def _onLoading(self):
        self.__updateModel()
        super(BattleSessionView, self)._onLoading()

    def __updateModel(self):
        with self.viewModel.transaction() as tx:
            isInClan = g_clanCache.isInClan
            if isInClan:
                tx.setClanName(g_clanCache.clanName)
                clanIcon = getClanEmblemURL(g_clanCache.clanDBID, EmblemSize.SIZE_32)
                tx.setClanIcon(clanIcon if clanIcon is not None else '')
            tx.setIsInClan(isInClan)
            tx.setIsTournamentLinkIGB(isTournamentEnabled())
        return

    def __tournamentsClickedHandler(self):
        if isTournamentEnabled():
            showTournaments()
        else:
            self.__openUrl(_TOURNAMENTS_URL)

    def __globalMapClickedHandler(self):
        self.__openUrl(_GLOBAL_MAP_URL)

    @staticmethod
    def __clanClickedHandler():
        event = g_entitiesFactories.makeLoadEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_STRONGHOLD))
        g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)

    def __closeClickedHandler(self):
        self.destroyWindow()

    @adisp_process
    def __openUrl(self, name):
        url = yield self.__externalLinks.getURL(name)
        self.__externalLinks.open(url)

    def __onServerSettingsChanged(self, diff):
        if TOURNAMENT_CONFIG in diff:
            self.__updateModel()
