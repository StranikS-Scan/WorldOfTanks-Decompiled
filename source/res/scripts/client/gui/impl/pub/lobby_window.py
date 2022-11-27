# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/lobby_window.py
import logging
import typing
from frameworks.wulf import Window, WindowSettings, WindowFlags, WindowLayer, WindowStatus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from frameworks.wulf import View
    from typing import Optional

class LobbyWindow(Window):
    __slots__ = ()
    __appLoader = dependency.descriptor(IAppLoader)
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self, wndFlags, decorator=None, content=None, parent=None, layer=WindowLayer.UNDEFINED):
        settings = WindowSettings()
        settings.flags = wndFlags
        settings.layer = layer
        settings.decorator = decorator
        settings.content = content
        settings.parent = self._getParent(parent, content)
        super(LobbyWindow, self).__init__(settings)

    @classmethod
    def getInstances(cls):
        return cls.__gui.windowsManager.findWindows(cls.__loadedWindowPredicate)

    def _getParent(self, parent, content):
        if parent:
            return parent
        else:
            app = self.__appLoader.getApp()
            containerMgr = app.containerManager
            if containerMgr is not None:
                view = containerMgr.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY))
                if view is not None:
                    return view.getParentWindow()
            _logger.error('LobbyWindow. Lobby view is not found for %r!', content)
            return

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

    def _getParent(self, parent, content):
        self.__initialParent = super(LobbyNotificationWindow, self)._getParent(parent, content)
        return None
