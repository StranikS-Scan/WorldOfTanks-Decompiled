# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_fade_view.py
import logging
import BigWorld
from frameworks.wulf import ViewFlags, ViewSettings
from frameworks.wulf import WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootboxes.loot_box_fade_view_model import LootBoxFadeViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import g_eventBus
from gui.shared.events import LootboxesEvent
from helpers import dependency
from skeletons.gui.game_control import IFestivityController
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class LootBoxFadeView(ViewImpl):
    lobbyContext = dependency.descriptor(ILobbyContext)
    _festivityController = dependency.descriptor(IFestivityController)
    __slots__ = ('__withPause',)

    def __init__(self, withPause=True):
        settings = ViewSettings(layoutID=R.views.lobby.loot_box.views.loot_box_fade_view.LootBoxFadeView(), flags=ViewFlags.VIEW, model=LootBoxFadeViewModel())
        super(LootBoxFadeView, self).__init__(settings)
        self.__withPause = withPause

    @property
    def viewModel(self):
        return super(LootBoxFadeView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(LootBoxFadeView, self)._initialize()
        self._festivityController.onStateChanged += self.__onStateChange
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.viewModel.onFadeInCompleted += self.__onFadeInCompleted
        self.viewModel.onWindowClose += self.__onWindowClose
        self.viewModel.onCloseClick += self.__onCloseClick
        if self.__withPause:
            g_eventBus.addListener(LootboxesEvent.REMOVE_HIDE_VIEW, self.__removeHideView, scope=EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.addListener(LootboxesEvent.ON_VIDEO_LOAD_ERROR, self.__onLoadError, scope=EVENT_BUS_SCOPE.LOBBY)
        with self.viewModel.transaction() as model:
            model.setWithPause(self.__withPause)
            model.setShowWindow(True)

    def _finalize(self):
        self._festivityController.onStateChanged -= self.__onStateChange
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.viewModel.onFadeInCompleted -= self.__onFadeInCompleted
        self.viewModel.onWindowClose -= self.__onWindowClose
        self.viewModel.onCloseClick -= self.__onCloseClick
        if self.__withPause:
            g_eventBus.removeListener(LootboxesEvent.REMOVE_HIDE_VIEW, self.__removeHideView, scope=EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.removeListener(LootboxesEvent.ON_VIDEO_LOAD_ERROR, self.__onLoadError, scope=EVENT_BUS_SCOPE.LOBBY)
        super(LootBoxFadeView, self)._finalize()

    def __onLoadError(self, _=None):
        self.viewModel.setShowError(True)

    def __onServerSettingChanged(self, diff):
        if not self.lobbyContext.getServerSettings().isLootBoxesEnabled():
            self.destroyWindow()

    def __onStateChange(self):
        if not self._festivityController.isEnabled():
            self.destroyWindow()

    def __onWindowClose(self, _=None):
        self.destroyWindow()

    def __onCloseClick(self, _=None):
        BigWorld.restartGame()

    def __onFadeInCompleted(self, _=None):
        g_eventBus.handleEvent(LootboxesEvent(LootboxesEvent.HIDE_COMPLETE), EVENT_BUS_SCOPE.LOBBY)
        if not self.__withPause:
            self.viewModel.setShowWindow(False)

    def __removeHideView(self, _=None):
        self.viewModel.setShowWindow(False)


class LootBoxFadeWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, withPause=True, parent=None):
        super(LootBoxFadeWindow, self).__init__(wndFlags=WindowFlags.SERVICE_WINDOW, content=LootBoxFadeView(withPause), parent=parent)
