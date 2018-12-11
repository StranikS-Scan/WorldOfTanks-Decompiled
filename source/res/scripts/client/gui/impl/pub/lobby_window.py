# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/lobby_window.py
from frameworks.wulf import Window
from gui.app_loader import g_appLoader
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS

class LobbyWindow(Window):
    __slots__ = ()

    def __init__(self, wndFlags, decorator, content=None, parent=None):
        if parent is None:
            app = g_appLoader.getApp()
            view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY))
            if view is not None:
                parent = view.getParentWindow()
        super(LobbyWindow, self).__init__(wndFlags, decorator, content, parent)
        return
