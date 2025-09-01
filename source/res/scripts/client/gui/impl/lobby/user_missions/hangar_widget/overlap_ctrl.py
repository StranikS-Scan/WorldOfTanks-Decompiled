# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/overlap_ctrl.py
from debug_utils import LOG_CURRENT_EXCEPTION
from frameworks.wulf import WindowStatus, WindowLayer
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.lobby.hangar.states import DefaultHangarState

class OverlapCtrlMixin(object):
    __RESTRICTED_LAYERS = (WindowLayer.FULLSCREEN_WINDOW,
     WindowLayer.OVERLAY,
     WindowLayer.TOP_WINDOW,
     WindowLayer.WINDOW,
     WindowLayer.TOP_SUB_VIEW)
    _MIN_WINDOW_WIDTH = 1000
    _MIN_WINDOW_HEIGHT = 600
    __ACTIVE_WINDOW_STATUSES = (WindowStatus.LOADING, WindowStatus.LOADED)

    def __init__(self, *args, **kwargs):
        self._lobbyStateMachine = None
        self._isInHangar = True
        self.__isWindowOverlapped = False
        self.__isUpdateQueued = False
        self.__deferredUpdates = []
        self.__isFullUpdate = False
        self._isFinalized = False
        self._updateWindowOverlapped()
        super(OverlapCtrlMixin, self).__init__(*args, **kwargs)
        return

    def deferUpdate(self, updMethod, *args, **kwargs):
        if self._isFinalized:
            return

        def updateLater():
            updMethod(*args, **kwargs)

        self.__deferredUpdates.append(updateLater)
        self.__isUpdateQueued = True

    def initOverlapCtrl(self):
        self._lobbyStateMachine = getLobbyStateMachine()

    @property
    def hasDeferModelUpdate(self):
        return not self._isInHangar or self.__isWindowOverlapped

    @property
    def isUpdateQueued(self):
        return self.__isUpdateQueued

    def queueUpdate(self):
        if self._isFinalized:
            return
        self.__isFullUpdate = True
        if not self.hasDeferModelUpdate:
            self._rawUpdate()

    def onWidgetUnmounted(self):
        self.queueUpdate()

    def _finalize(self):
        self._isFinalized = True
        del self.__deferredUpdates[:]
        super(OverlapCtrlMixin, self)._finalize()

    def _getEvents(self):
        return super(OverlapCtrlMixin, self)._getEvents() + ((self._lobbyStateMachine.onVisibleRouteChanged, self._onVisibleRouteChanged), (self.gui.windowsManager.onWindowStatusChanged, self._onWindowStatusChanged))

    def _onVisibleRouteChanged(self, routeInfo):
        self._isInHangar = routeInfo.state == self._lobbyStateMachine.getStateByCls(DefaultHangarState)
        self._updateViewModelIfNeeded()

    def _onWindowStatusChanged(self, _, newStatus):
        if newStatus in (WindowStatus.LOADING, WindowStatus.LOADED, WindowStatus.DESTROYING):
            self._updateWindowOverlapped()
            self._updateViewModelIfNeeded()

    def _updateWindowOverlapped(self):

        def _isValidWindowSize(window):
            size = window.size
            return size[0] > self._MIN_WINDOW_WIDTH and size[1] > self._MIN_WINDOW_HEIGHT

        windows = self.gui.windowsManager.findWindows(lambda w: w.layer in self.__RESTRICTED_LAYERS and w.windowStatus in self.__ACTIVE_WINDOW_STATUSES and _isValidWindowSize(w))
        self.__isWindowOverlapped = bool(windows)

    def _rawUpdate(self):
        self.__isFullUpdate = False

    def _updateAll(self):
        for call in self.__deferredUpdates:
            try:
                call()
            except Exception:
                LOG_CURRENT_EXCEPTION()

        self.__isUpdateQueued = False

    def _updateViewModelIfNeeded(self):
        if self.hasDeferModelUpdate or not (self.__isUpdateQueued or self.__isFullUpdate):
            return
        self.__isUpdateQueued = False
        if self.__isFullUpdate:
            self._rawUpdate()
        elif self.__deferredUpdates:
            self._updateAll()
        del self.__deferredUpdates[:]
