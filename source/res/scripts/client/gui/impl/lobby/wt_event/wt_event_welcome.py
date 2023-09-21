# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_welcome.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_welcome_model import WtEventWelcomeModel
from gui.impl.pub import ViewImpl
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.managers.view_lifecycle_watcher import IViewLifecycleHandler, ViewLifecycleWatcher
from gui.shared.event_dispatcher import showBrowserOverlayView, showEventProgressionWindow
from gui.wt_event.wt_event_helpers import getIntroVideoURL
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IEventBattlesController

class _WTEventWelcomeViewLifecycleHandler(IViewLifecycleHandler):

    def __init__(self, parentView):
        super(_WTEventWelcomeViewLifecycleHandler, self).__init__([ViewKey(VIEW_ALIAS.BROWSER_OVERLAY)])
        self.__parentView = parentView

    def onViewDestroyed(self, view):
        self.__parentView.onVideoClosed()


class WTEventWelcomeView(ViewImpl):
    __slots__ = ('__viewLifecycleWatcher',)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __eventCtrl = dependency.descriptor(IEventBattlesController)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WTEventWelcome(), flags=ViewFlags.LOBBY_TOP_SUB_VIEW, model=WtEventWelcomeModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WTEventWelcomeView, self).__init__(settings)
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()

    @property
    def viewModel(self):
        return self.getViewModel()

    def onVideoClosed(self):
        self.viewModel.setIsVideoOpened(False)

    def _onLoading(self, *args, **kwargs):
        Waiting.show('loadPage')
        super(WTEventWelcomeView, self)._onLoading()
        self.__addListeners()

    def _onLoaded(self, *args, **kwargs):
        super(WTEventWelcomeView, self)._onLoaded(*args, **kwargs)
        Waiting.hide('loadPage')
        app = self.__appLoader.getApp()
        self.__viewLifecycleWatcher.start(app.containerManager, [_WTEventWelcomeViewLifecycleHandler(self)])

    def _finalize(self):
        self.__removeListeners()
        self.__viewLifecycleWatcher.stop()
        self.__viewLifecycleWatcher = None
        super(WTEventWelcomeView, self)._finalize()
        return

    def __addListeners(self):
        self.viewModel.onVideo += self.__showIntroVideo
        self.viewModel.onClose += self.__onCloseHandler
        self.__eventCtrl.onEventPrbChanged += self.__onEventPrbChanged

    def __removeListeners(self):
        self.viewModel.onVideo -= self.__showIntroVideo
        self.viewModel.onClose -= self.__onCloseHandler
        self.__eventCtrl.onEventPrbChanged -= self.__onEventPrbChanged

    def __onCloseHandler(self):
        if self.__eventCtrl.isAvailable():
            showEventProgressionWindow(fromWelcome=True)
        self.destroyWindow()

    def __showIntroVideo(self, onStart=False):
        self.viewModel.setIsVideoOpened(True)
        showBrowserOverlayView(getIntroVideoURL(), VIEW_ALIAS.BROWSER_OVERLAY, forcedSkipEscape=True)

    def __onEventPrbChanged(self, isActive):
        if not isActive:
            self.destroyWindow()
