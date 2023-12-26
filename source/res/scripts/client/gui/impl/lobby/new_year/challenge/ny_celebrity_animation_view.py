# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/challenge/ny_celebrity_animation_view.py
from frameworks.wulf import ViewSettings, WindowLayer
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.new_year.navigation import NewYearNavigation
from frameworks.wulf import ViewModel
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import NyCelebrityAnimationEvent, NyGladeVisibilityEvent, LobbySimpleEvent
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared.utils import IHangarSpace
from helpers import dependency
_CHANGE_LAYERS_VISIBILITY = (WindowLayer.VIEW, WindowLayer.WINDOW)

class NyCelebrityAnimationView(ViewImpl):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    __appLoader = dependency.instance(IAppLoader)

    def __init__(self, justReceived, previewType):
        settings = ViewSettings(R.views.lobby.new_year.CelebrityAnimationView())
        settings.model = ViewModel()
        self.__justReceived = justReceived
        self.__previewType = previewType
        super(NyCelebrityAnimationView, self).__init__(settings)

    def _getListeners(self):
        listeners = super(NyCelebrityAnimationView, self)._getListeners()
        return listeners + ((NyCelebrityAnimationEvent.CLOSE_ANIMATION_VIEW, self.__handleCloseView, EVENT_BUS_SCOPE.DEFAULT),)

    def _initialize(self):
        super(NyCelebrityAnimationView, self)._initialize()
        self._hangarSpace.setSelectionEnabled(False)
        self.__changeLayersVisibility(True, _CHANGE_LAYERS_VISIBILITY)
        NewYearNavigation.onObjectStateChanged += self.__onNavigation

    def _onLoaded(self, *args, **kwargs):
        super(NyCelebrityAnimationView, self)._onLoaded(args, kwargs)
        g_eventBus.handleEvent(NyGladeVisibilityEvent(eventType=NyGladeVisibilityEvent.START_FADE_IN), scope=EVENT_BUS_SCOPE.DEFAULT)
        g_eventBus.handleEvent(NyCelebrityAnimationEvent(eventType=NyCelebrityAnimationEvent.ANIMATION_VIEW_OPENED), scope=EVENT_BUS_SCOPE.DEFAULT)
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.MESSENGER_BAR_VISIBLE, ctx={'visible': False}), scope=EVENT_BUS_SCOPE.LOBBY)
        if not NewYearNavigation.getCurrentObject():
            self.destroyWindow()

    def _finalize(self):
        self._hangarSpace.setSelectionEnabled(True)
        g_eventBus.handleEvent(NyGladeVisibilityEvent(eventType=NyGladeVisibilityEvent.START_FADE_OUT), scope=EVENT_BUS_SCOPE.DEFAULT)
        g_eventBus.handleEvent(NyCelebrityAnimationEvent(eventType=NyCelebrityAnimationEvent.ANIMATION_VIEW_CLOSED, ctx={'justReceived': self.__justReceived,
         'previewType': self.__previewType}), scope=EVENT_BUS_SCOPE.DEFAULT)
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.MESSENGER_BAR_VISIBLE, ctx={'visible': True}), scope=EVENT_BUS_SCOPE.LOBBY)
        self.__changeLayersVisibility(False, _CHANGE_LAYERS_VISIBILITY)
        NewYearNavigation.onObjectStateChanged -= self.__onNavigation
        super(NyCelebrityAnimationView, self)._finalize()

    def __handleCloseView(self, _):
        self.destroyWindow()

    def __onNavigation(self):
        self.destroyWindow()

    def __changeLayersVisibility(self, isHide, layers):
        lobby = self.__appLoader.getDefLobbyApp()
        if lobby:
            if isHide:
                lobby.containerManager.hideContainers(layers, time=0.3)
            else:
                lobby.containerManager.showContainers(layers, time=0.3)
            self.__appLoader.getApp().graphicsOptimizationManager.switchOptimizationEnabled(not isHide)


class NyCelebrityAnimationWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, justReceived=None, previewType=None, parent=None):
        super(NyCelebrityAnimationWindow, self).__init__(content=NyCelebrityAnimationView(justReceived, previewType), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)
