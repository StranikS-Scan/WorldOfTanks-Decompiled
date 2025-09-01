# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/main_menu_presenter.py
from __future__ import absolute_import
import logging
import typing
from constants import GF_RES_PROTOCOL, PremiumConfigs, DAILY_QUESTS_CONFIG
from PlayerEvents import g_playerEvents
from gui.clans.clan_cache import g_clanCache
from gui.impl.gen.view_models.views.lobby.hangar.main_menu_model import MainMenuModel
from gui.impl.lobby.hangar.presenters.utils import fillMenuItems
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.image_helper import getTextureLinkByID
from gui.shared.view_helpers import ClanEmblemsHelper
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.techtree_events import ITechTreeEventsListener
if typing.TYPE_CHECKING:
    from collections import OrderedDict
_logger = logging.getLogger(__name__)

class MainMenuPresenter(ViewComponent[MainMenuModel], ClanEmblemsHelper, IGlobalListener):
    __techTreeEventsListener = dependency.descriptor(ITechTreeEventsListener)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, menuItems):
        super(MainMenuPresenter, self).__init__(model=MainMenuModel)
        self.__menuItems = menuItems
        self.__clanIconID = None
        return

    @property
    def viewModel(self):
        return super(MainMenuPresenter, self).getViewModel()

    def onClanEmblem32x32Received(self, clanDbID, emblem):
        self.__removeClanIconFromMemory()
        if emblem:
            self.__clanIconID = self.getMemoryTexturePath(emblem, temp=False)
            self.viewModel.setClanEmblem(getTextureLinkByID(self.__clanIconID, GF_RES_PROTOCOL.CACHED_IMG))
        else:
            self.viewModel.setClanEmblem('')

    def onPrbEntitySwitched(self, _=None):
        self.__updateModel()

    def _getEvents(self):
        return super(MainMenuPresenter, self)._getEvents() + ((self.viewModel.onNavigate, self._navigateTo), (g_playerEvents.onPrebattleJoined, self.__updateModel), (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged))

    def _getCallbacks(self):
        return (('stats.clanInfo', self.__requestClanEmblem),) if self.__clansMenuItemExists() else tuple()

    def _navigateTo(self, args):
        name = args.get('name')
        menuEntry = self.__menuItems.get(name)
        menuEntry.handler()

    def _onLoading(self, *args, **kwargs):
        super(MainMenuPresenter, self)._onLoading()
        self.startGlobalListening()
        if self.__clansMenuItemExists():
            self.__requestClanEmblem()
        self.__updateModel()

    def _finalize(self):
        self.stopGlobalListening()
        if self.__clansMenuItemExists():
            self.__removeClanIconFromMemory()
        super(MainMenuPresenter, self)._finalize()

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            fillMenuItems(model, self.__menuItems)
            if self.__techTreeEventsListener.getNations():
                model.setHasTechTreeEvents(True)

    def __requestClanEmblem(self, *_):
        if g_clanCache.clanDBID:
            self.requestClanEmblem32x32(g_clanCache.clanDBID)
        else:
            self.__removeClanIconFromMemory()
            self.viewModel.setClanEmblem('')

    def __removeClanIconFromMemory(self):
        if self.__clanIconID is not None:
            self.removeTextureFromMemory(self.__clanIconID)
            self.__clanIconID = None
        return

    def __clansMenuItemExists(self):
        return self.__menuItems.get(MainMenuModel.CLANS) is not None

    def __onServerSettingsChanged(self, diff=None):
        diff = diff or {}
        settingsKeys = [DAILY_QUESTS_CONFIG,
         PremiumConfigs.PREM_QUESTS,
         'strongholdSettings',
         'isRegularQuestEnabled',
         'isPM2QuestEnabled',
         'isPM3QuestEnabled']
        if any((key in diff for key in settingsKeys)):
            self.__updateModel()
