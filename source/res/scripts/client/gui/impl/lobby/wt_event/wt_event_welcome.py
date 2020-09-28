# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_welcome.py
import BigWorld
from frameworks.wulf import ViewFlags, WindowFlags, ViewSettings
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_welcome_model import WtEventWelcomeModel
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.event_dispatcher import showBrowserOverlayView, showWtEventCollectionWindow
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.managers.view_lifecycle_watcher import IViewLifecycleHandler, ViewLifecycleWatcher
from gui.wt_event.wt_event_helpers import getIntroVideoURL
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IGameEventController

class _WTEventWelcomeViewLifecycleHandler(IViewLifecycleHandler):

    def __init__(self, parentView):
        super(_WTEventWelcomeViewLifecycleHandler, self).__init__([ViewKey(VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB)])
        self.__parentView = parentView

    def onViewDestroyed(self, view):
        self.__parentView.onVideoClosed()


class WTEventWelcomeView(ViewImpl):
    __slots__ = ('__viewLifecycleWatcher', '__waitingTimeout', '__isCollectionShown')
    __appLoader = dependency.descriptor(IAppLoader)
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WTEventWelcome(), flags=ViewFlags.LOBBY_TOP_SUB_VIEW, model=WtEventWelcomeModel())
        settings.args = args
        settings.kwargs = kwargs
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()
        self.__waitingTimeout = 1.0
        self.__isCollectionShown = False
        super(WTEventWelcomeView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        Waiting.show('loadPage')
        BigWorld.callback(self.__waitingTimeout, self.__hideWaiting)
        super(WTEventWelcomeView, self)._onLoading()
        self.__addListeners()

    def _onLoaded(self, *args, **kwargs):
        super(WTEventWelcomeView, self)._onLoaded(*args, **kwargs)
        app = self.__appLoader.getApp()
        self.__viewLifecycleWatcher.start(app.containerManager, [_WTEventWelcomeViewLifecycleHandler(self)])

    def __hideWaiting(self):
        Waiting.hide('loadPage')

    def _finalize(self):
        if not self.__isCollectionShown:
            self.__gameEventController.onEventWelcomeCollectionScreensClosed()
        self.__removeListeners()
        self.__viewLifecycleWatcher.stop()

    @property
    def viewModel(self):
        return super(WTEventWelcomeView, self).getViewModel()

    def onVideoClosed(self):
        self.viewModel.setIsVideoOpened(False)

    def __addListeners(self):
        self.viewModel.onVideo += self.__showIntroVideo
        self.viewModel.onClose += self.__onCloseHandler
        self.__gameEventController.onEventPrbChanged += self.__onEventPrbChanged

    def __removeListeners(self):
        self.__gameEventController.onEventPrbChanged -= self.__onEventPrbChanged
        self.viewModel.onVideo -= self.__showIntroVideo
        self.viewModel.onClose -= self.__onCloseHandler

    def __onCloseHandler(self):
        if self.__gameEventController.isEventPrbActive():
            showWtEventCollectionWindow(fromWelcome=True)
            self.__isCollectionShown = True
        self.destroyWindow()

    def __showIntroVideo(self, onStart=False):
        self.viewModel.setIsVideoOpened(True)
        showBrowserOverlayView(getIntroVideoURL())

    def __onEventPrbChanged(self, isActive):
        if not isActive:
            self.destroyWindow()


class WTEventWelcomeWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(WTEventWelcomeWindow, self).__init__(WindowFlags.WINDOW, content=WTEventWelcomeView(), parent=parent)
