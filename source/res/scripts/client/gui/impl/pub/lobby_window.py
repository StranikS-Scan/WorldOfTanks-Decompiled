# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/lobby_window.py
from frameworks.wulf import Window, WindowSettings, WindowFlags
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IOverlaysManager

class LobbyWindow(Window):
    __slots__ = ()
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, wndFlags, decorator, content=None, parent=None):
        if parent is None:
            app = self.__appLoader.getApp()
            view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY))
            if view is not None:
                parent = view.getParentWindow()
        settings = WindowSettings()
        settings.flags = wndFlags
        settings.decorator = decorator
        settings.content = content
        settings.parent = parent
        super(LobbyWindow, self).__init__(settings)
        return


class OverlayBehaviorFlags(object):
    DEFAULT = 0
    IS_EXCLUSIVE = 1
    IS_REPEATABLE = 2


class OverlayBehavior(object):
    __slots__ = ('_flags',)

    def __init__(self, flags=OverlayBehaviorFlags.DEFAULT):
        super(OverlayBehavior, self).__init__()
        self._flags = flags

    @property
    def isExclusive(self):
        return self._flags & OverlayBehaviorFlags.IS_EXCLUSIVE > 0

    @property
    def isRepeatable(self):
        return self._flags & OverlayBehaviorFlags.IS_REPEATABLE > 0

    def close(self, window):
        pass

    def repeat(self):
        return None


class LobbyOverlay(LobbyWindow):
    __slots__ = ('__behavior',)
    __overlays = dependency.descriptor(IOverlaysManager)

    def __init__(self, behavior=None, decorator=None, content=None, parent=None):
        if behavior is None:
            behavior = OverlayBehavior()
        self.__behavior = behavior
        super(LobbyOverlay, self).__init__(wndFlags=WindowFlags.OVERLAY, decorator=decorator, content=content, parent=parent)
        return

    @property
    def behavior(self):
        return self.__behavior

    def load(self):
        if not self.__overlays.isSuspended(self):
            super(LobbyOverlay, self).load()
