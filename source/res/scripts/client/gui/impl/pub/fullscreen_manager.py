# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/fullscreen_manager.py
import logging
import weakref
import typing
from frameworks.state_machine import SingleStateObserver
from frameworks.wulf import WindowLayer, WindowStatus
from gui.impl.lobby.platoon.platoon_helpers import PreloadableWindow
from helpers import dependency
from skeletons.gameplay import GameplayStateID, IGameplayLogic
from skeletons.gui.impl import IGuiLoader, IFullscreenManager, INotificationWindowController
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.sf_window import SFWindow
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window
_logger = logging.getLogger(__name__)
_LOW_PRIORITY_WINDOWS = (VIEW_ALIAS.AWARD_WINDOW, VIEW_ALIAS.AWARD_WINDOW_MODAL, VIEW_ALIAS.ADVENT_CALENDAR)

class FullscreenManager(IFullscreenManager):
    __slots__ = ('__gui', '__notificationMgr', '__isEnabled', '__weakref__', '__observer', '__gameplay')
    __gui = dependency.descriptor(IGuiLoader)
    __gameplay = dependency.descriptor(IGameplayLogic)
    __notificationMgr = dependency.descriptor(INotificationWindowController)

    def __init__(self):
        super(FullscreenManager, self).__init__()
        self.__observer = _LobbyStateObserver(weakref.proxy(self))
        self.__isEnabled = False

    def init(self):
        self.__gameplay.addStateObserver(self.__observer)

    def fini(self):
        self.setEnabled(False)
        self.__gameplay.removeStateObserver(self.__observer)
        self.__observer.clear()

    def setEnabled(self, value):
        _logger.debug('Manager enabled=%r', value)
        self.__isEnabled = value
        if value:
            self.__gui.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged
        else:
            self.__gui.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged

    def __onWindowStatusChanged(self, uniqueID, newState):
        window = self.__gui.windowsManager.getWindow(uniqueID)
        if newState == WindowStatus.LOADING:
            self.__onWindowOpen(window)
        if newState == WindowStatus.LOADED:
            self.__onWindowsOpened(window)

    def __onWindowOpen(self, newWindow):
        if isinstance(newWindow, PreloadableWindow) and newWindow.isPreloading:
            return
        layer = newWindow.layer
        if not WindowLayer.VIEW <= layer <= WindowLayer.FULLSCREEN_WINDOW:
            return
        windows = self.__gui.windowsManager.findWindows(self.__fullscreenPredicate)
        windowsToClose = []
        for window in windows:
            if window != newWindow and (window.layer > layer or window.layer == layer) and not self.__isParent(window, newWindow) and self.__isAllowed(newWindow):
                windowsToClose.append(window)

        if (not windows or windowsToClose) and not self.__notificationMgr.hasWindow(newWindow) and self.__isAllowed(newWindow):
            _logger.info('Notification queue postpones by opening window %r', newWindow)
            self.__notificationMgr.postponeActive()
        for window in windowsToClose:
            _logger.info('Window %r has been destroyed by opening window %r', window, newWindow)
            window.destroy()

    def __onWindowsOpened(self, newWindow):
        layer = newWindow.layer
        if layer != WindowLayer.FULLSCREEN_WINDOW:
            return
        newWindow.bringToFront()

    @classmethod
    def __isParent(cls, pWindow, window):
        if window.parent is None:
            return False
        else:
            return True if window.parent == pWindow else cls.__isParent(pWindow, window.parent)

    @staticmethod
    def __fullscreenPredicate(window):
        return window.layer == WindowLayer.FULLSCREEN_WINDOW and window.windowStatus in (WindowStatus.LOADING, WindowStatus.LOADED)

    @staticmethod
    def __isAllowed(window):
        if isinstance(window, SFWindow):
            alias = window.loadParams.viewKey.alias
            for priority in _LOW_PRIORITY_WINDOWS:
                if alias.startswith(priority):
                    return False

        return True


class _LobbyStateObserver(SingleStateObserver):
    __slots__ = ('__manager', '__gui')
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self, manager):
        super(_LobbyStateObserver, self).__init__(GameplayStateID.ACCOUNT)
        self.__manager = manager

    def onEnterState(self, event=None):
        super(_LobbyStateObserver, self).onEnterState(event)
        self.__gui.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged

    def onExitState(self, event=None):
        super(_LobbyStateObserver, self).onExitState(event)
        self.__gui.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged
        self.__manager.setEnabled(False)

    def clear(self):
        super(_LobbyStateObserver, self).clear()
        self.__gui.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged
        self.__manager = None
        return

    def __onWindowStatusChanged(self, uniqueID, newStatus):
        if newStatus == WindowStatus.LOADED:
            window = self.__gui.windowsManager.getWindow(uniqueID)
            if window.layer == WindowLayer.SUB_VIEW:
                self.__gui.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged
                self.__manager.setEnabled(True)
