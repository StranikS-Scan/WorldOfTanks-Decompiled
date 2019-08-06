# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/lobby_window.py
from frameworks.wulf import Window, WindowSettings
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader

class LobbyWindow(Window):
    __slots__ = ()
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, wndFlags, decorator=None, content=None, parent=None):
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
