# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/intro_view.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import RTS_INTRO_PAGE_VISITED
from frameworks.wulf import ViewSettings, ViewFlags
from gui import GUI_SETTINGS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.rts.intro_view_model import IntroViewModel
from gui.impl.pub import ViewImpl
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.view_lifecycle_watcher import IViewLifecycleHandler, ViewLifecycleWatcher
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showBrowserOverlayView, showRTSMetaRootWindow
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IRTSBattlesController

class _RtsIntroViewLifecycleHandler(IViewLifecycleHandler):

    def __init__(self, parentView):
        super(_RtsIntroViewLifecycleHandler, self).__init__([ViewKey(VIEW_ALIAS.BROWSER_OVERLAY)])
        self.__parentView = parentView

    def onViewDestroyed(self, view):
        self.__parentView.onVideoClosed()


class IntroView(ViewImpl):
    __slots__ = ('__viewLifecycleWatcher',)
    __appLoader = dependency.descriptor(IAppLoader)
    __rtsController = dependency.descriptor(IRTSBattlesController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.rts.IntroView(), model=IntroViewModel(), flags=ViewFlags.LOBBY_TOP_SUB_VIEW)
        settings.args = args
        settings.kwargs = kwargs
        super(IntroView, self).__init__(settings)
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()

    @property
    def viewModel(self):
        return super(IntroView, self).getViewModel()

    def onVideoClosed(self):
        self.viewModel.setIsVideoOpened(False)

    def _onLoading(self, *args, **kwargs):
        Waiting.show('loadPage')
        super(IntroView, self)._onLoading()
        self._addListeners()

    def _onLoaded(self, *args, **kwargs):
        super(IntroView, self)._onLoaded(*args, **kwargs)
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), EVENT_BUS_SCOPE.LOBBY)
        Waiting.hide('loadPage')
        app = self.__appLoader.getApp()
        self.__viewLifecycleWatcher.start(app.containerManager, [_RtsIntroViewLifecycleHandler(self)])
        AccountSettings.setNotifications(RTS_INTRO_PAGE_VISITED, True)

    def _initialize(self, *args, **kwargs):
        soundManager = self.__rtsController.getSoundManager()
        soundManager.onOpenPage()

    def _finalize(self):
        soundManager = self.__rtsController.getSoundManager()
        soundManager.onClosePage()
        self.__viewLifecycleWatcher.stop()
        self.__viewLifecycleWatcher = None
        self._removeListeners()
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
        super(IntroView, self)._finalize()
        return

    def _onVideo(self):
        self.viewModel.setIsVideoOpened(True)
        showBrowserOverlayView(GUI_SETTINGS.rtsIntroVideoURL, VIEW_ALIAS.BROWSER_OVERLAY, forcedSkipEscape=True)

    def _addListeners(self):
        self.viewModel.onClose += self.__onCloseHandler
        self.viewModel.onVideo += self._onVideo

    def _removeListeners(self):
        self.viewModel.onClose -= self.__onCloseHandler
        self.viewModel.onVideo -= self._onVideo

    def __onCloseHandler(self):
        Waiting.show('loadPage')
        self.destroyWindow()
        showRTSMetaRootWindow()
