# Embedded file name: scripts/client/gui/game_control/ChinaController.py
import weakref
import constants
from gui.Scaleform.locale.MENU import MENU
from gui.shared import g_eventBus, events

class ChinaController(object):
    BROWSER_COUNT = 999

    def __init__(self, proxy):
        self.__proxy = weakref.proxy(proxy)
        self.__browserID = None
        return

    def start(self):
        g_eventBus.addListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__handleLobbyLoaded)

    def stop(self):
        self.__browserID = None
        g_eventBus.removeListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__handleLobbyLoaded)
        return

    def showBrowser(self):
        self.__browserID = self._getBrowserController().load(title=MENU.BROWSER_WINDOW_TITLE, browserID=self.__browserID)

    def _getBrowserController(self):
        return self.__proxy.browser

    def __handleLobbyLoaded(self, *args):
        if constants.IS_CHINA:
            if not self.__proxy.gameSession.battlesCount % self.BROWSER_COUNT:
                self.showBrowser()
