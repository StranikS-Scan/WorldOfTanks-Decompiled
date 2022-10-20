# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/lobby_window.py
import typing
from frameworks.wulf import Window, WindowSettings, WindowFlags, WindowLayer, WindowStatus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.game_control import IEventBattlesController
if typing.TYPE_CHECKING:
    from frameworks.wulf import View
    from typing import Optional

class LobbyWindow(Window):
    __slots__ = ('_isEventHangar',)
    __appLoader = dependency.descriptor(IAppLoader)
    __gui = dependency.descriptor(IGuiLoader)
    _eventBattlesController = dependency.descriptor(IEventBattlesController)

    def __init__(self, wndFlags, decorator=None, content=None, parent=None, layer=WindowLayer.UNDEFINED):
        settings = WindowSettings()
        settings.flags = wndFlags
        settings.layer = layer
        settings.decorator = decorator
        settings.content = content
        settings.parent = self._getParent(parent)
        self._isEventHangar = False
        super(LobbyWindow, self).__init__(settings)

    @classmethod
    def getInstances(cls):
        return cls.__gui.windowsManager.findWindows(cls.__loadedWindowPredicate)

    def _initialize(self):
        super(LobbyWindow, self)._initialize()
        self._isEventHangar = self._eventBattlesController.isEventHangar()
        if self._isEventHangar:
            self._eventBattlesController.onEventDisabled += self._onEventDisabled

    def _finalize(self):
        if self._isEventHangar:
            self._eventBattlesController.onEventDisabled -= self._onEventDisabled
        super(LobbyWindow, self)._finalize()

    def _onEventDisabled(self):
        if self._isEventHangar:
            self.destroy()

    def _getParent(self, parent):
        if parent:
            return parent
        else:
            app = self.__appLoader.getApp()
            view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY))
            return view.getParentWindow() if view is not None else None

    @classmethod
    def __loadedWindowPredicate(cls, window):
        return window.windowStatus == WindowStatus.LOADED and isinstance(window, cls)


class LobbyNotificationWindow(LobbyWindow):
    __slots__ = ('__initialParent',)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, wndFlags=None, decorator=None, content=None, parent=None, layer=WindowLayer.UNDEFINED):
        self.__initialParent = None
        flags = wndFlags or WindowFlags.SERVICE_WINDOW | WindowFlags.WINDOW_FULLSCREEN
        flags = flags | WindowFlags.WINDOW_MODAL
        super(LobbyNotificationWindow, self).__init__(flags, decorator, content, parent, layer)
        return

    def load(self):
        if self.__initialParent is not None:
            self.setParent(self.__initialParent)
        super(LobbyNotificationWindow, self).load()
        return

    def _getParent(self, parent):
        self.__initialParent = super(LobbyNotificationWindow, self)._getParent(parent)
        return None
