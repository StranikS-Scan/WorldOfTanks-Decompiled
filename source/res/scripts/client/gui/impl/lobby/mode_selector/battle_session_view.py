# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/battle_session_view.py
from adisp import adisp_process
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.battle_session_model import BattleSessionModel
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.ClanCache import g_clanCache
from gui.shared.view_helpers.emblems import getClanEmblemURL, EmblemSize
from helpers import dependency
from skeletons.gui.game_control import IExternalLinksController
_TOURNAMENTS_URL = 'tournamentsURL'
_GLOBAL_MAP_URL = 'globalMapURL'

class BattleSessionView(ViewImpl):
    __slots__ = ()
    layoutID = R.views.lobby.mode_selector.BattleSessionView()
    __externalLinks = dependency.descriptor(IExternalLinksController)

    def __init__(self, layoutID):
        super(BattleSessionView, self).__init__(ViewSettings(layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, BattleSessionModel()))

    def _onLoading(self):
        viewModel = self.getViewModel()
        isInClan = g_clanCache.isInClan
        if isInClan:
            viewModel.setClanName(g_clanCache.clanName)
            viewModel.setClanIcon(getClanEmblemURL(g_clanCache.clanDBID, EmblemSize.SIZE_32))
        viewModel.setIsInClan(isInClan)
        viewModel.onClanClicked += self.__clanClickedHandler
        viewModel.onTournamentsClicked += self.__tournamentsClickedHandler
        viewModel.onGlobalMapClicked += self.__globalMapClickedHandler
        viewModel.onCloseClicked += self.__closeClickedHandler

    def _finalize(self):
        viewModel = self.getViewModel()
        viewModel.onClanClicked -= self.__clanClickedHandler
        viewModel.onTournamentsClicked -= self.__tournamentsClickedHandler
        viewModel.onGlobalMapClicked -= self.__globalMapClickedHandler
        viewModel.onCloseClicked -= self.__closeClickedHandler

    def __tournamentsClickedHandler(self):
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
