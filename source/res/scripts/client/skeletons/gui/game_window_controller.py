# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/game_window_controller.py
from adisp import process, async
from gui.game_control.links import URLMacros
from helpers import dependency
from skeletons.gui.game_control import IGameWindowController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache

class GameWindowController(IGameWindowController):
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__urlMacros = URLMacros()
        super(GameWindowController, self).__init__()

    def fini(self):
        self.__urlMacros.clear()
        self.__urlMacros = None
        self.hideWindow()
        super(GameWindowController, self).fini()
        return

    def onLobbyInited(self, event):
        self._addListeners()

    def onAvatarBecomePlayer(self):
        self._removeListeners()
        self.hideWindow()
        super(GameWindowController, self).onAvatarBecomePlayer()

    def onDisconnected(self):
        self._removeListeners()
        self.hideWindow()
        super(GameWindowController, self).onDisconnected()

    def hideWindow(self):
        raise NotImplementedError

    def showWindow(self, url=None, invokedFrom=None):
        self.hideWindow()
        self._showWindow(url, invokedFrom)

    @async
    @process
    def getUrl(self, callback=lambda *args: None):
        url = yield self.__urlMacros.parse(self._getUrl())
        callback(url)

    def _addListeners(self):
        self.eventsCache.onSyncCompleted += self._onSyncCompleted

    def _removeListeners(self):
        self.eventsCache.onSyncCompleted -= self._onSyncCompleted

    def _onSyncCompleted(self, *_):
        pass

    @process
    def _showWindow(self, url, invokedFrom=None):
        if url is None:
            url = yield self.getUrl()
            if not url:
                return
        self._openWindow(url, invokedFrom)
        return

    def _openWindow(self, url, invokedFrom=None):
        raise NotImplementedError
