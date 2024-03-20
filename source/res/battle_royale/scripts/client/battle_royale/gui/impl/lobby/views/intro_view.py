# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/intro_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import currentHangarIsBattleRoyale
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattleRoyaleController, IHangarSpaceSwitchController
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.events import ViewEventType
from battle_royale.gui.Scaleform.daapi.view.lobby.battle_royale_sounds import Sounds
import SoundGroups
from battle_royale.gui.impl.gen.view_models.views.lobby.views.intro_view_model import IntroViewModel

class IntroView(ViewImpl, IGlobalListener):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __spaceSwitchController = dependency.descriptor(IHangarSpaceSwitchController)

    def __init__(self):
        settings = ViewSettings(R.views.battle_royale.lobby.views.IntroView())
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = IntroViewModel()
        self.__urlIntroVideo = self.__battleRoyaleController.getIntroVideoURL()
        self.__isPageWasShow = False
        super(IntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(IntroView, self).getViewModel()

    def onPrbEntitySwitched(self):
        if not self.__battleRoyaleController.isBattleRoyaleMode():
            self.destroyWindow()

    def _onLoading(self, *args, **kwargs):
        super(IntroView, self)._onLoading(*args, **kwargs)
        self.viewModel.onClose += self.__onClose
        self.viewModel.onShowVideo += self.__onShowVideo
        g_eventBus.addListener(ViewEventType.LOAD_VIEW, self.__handleLoadView, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.PrebattleEvent.SWITCHED, self.__onClose, scope=EVENT_BUS_SCOPE.LOBBY)
        if currentHangarIsBattleRoyale():
            self.__onSpaceUpdated()
        else:
            self.__spaceSwitchController.onSpaceUpdated += self.__onSpaceUpdated
        self.startGlobalListening()
        self.__updateViewModel()

    def _finalize(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onShowVideo -= self.__onShowVideo
        self.__spaceSwitchController.onSpaceUpdated -= self.__onSpaceUpdated
        g_eventBus.removeListener(events.PrebattleEvent.SWITCHED, self.__onClose, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self.__handleLoadView, scope=EVENT_BUS_SCOPE.LOBBY)
        self.stopGlobalListening()
        super(IntroView, self)._finalize()

    def __handleLoadView(self, event):
        if event.alias == VIEW_ALIAS.LOBBY_HANGAR:
            self.__onClose()

    def __onClose(self, *_):
        self.destroyWindow()

    def __onShowVideo(self):
        showBrowserOverlayView(self.__urlIntroVideo, VIEW_ALIAS.BROWSER_OVERLAY, callbackOnLoad=self.__onBrowserLoaded)

    def __onBrowserLoaded(self):
        SoundGroups.g_instance.playSound2D(Sounds.MUTE_EVENT)

    def __onSpaceUpdated(self):
        if not self.__isPageWasShow:
            self.__isPageWasShow = True
            self.__onShowVideo()
        else:
            self.__onClose()

    def __updateViewModel(self):
        with self.viewModel.transaction() as tx:
            tx.setStartDate(self.__battleRoyaleController.getStartTime())
            tx.setEndDate(self.__battleRoyaleController.getEndTime())


class IntroWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, ctx, parent):
        super(IntroWindow, self).__init__(content=IntroView(), wndFlags=WindowFlags.WINDOW, decorator=None, parent=parent)
        return
