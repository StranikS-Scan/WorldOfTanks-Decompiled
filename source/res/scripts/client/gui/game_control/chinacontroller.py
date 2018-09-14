# Embedded file name: scripts/client/gui/game_control/ChinaController.py
from adisp import process
from gui.Scaleform.locale.MENU import MENU
from gui.game_control import gc_constants
from gui.game_control.controllers import Controller

class ChinaController(Controller):

    def __init__(self, proxy):
        super(ChinaController, self).__init__(proxy)
        self.__browserID = None
        return

    def onLobbyInited(self, event):
        if not self._proxy.gameSession.battlesCount % gc_constants.BROWSER.CHINA_BROWSER_COUNT:
            self.showBrowser()

    def onDisconnected(self):
        self.__browserID = None
        return

    @process
    def showBrowser(self):
        self.__browserID = yield self._getBrowserController().load(title=MENU.BROWSER_WINDOW_TITLE, browserID=self.__browserID)

    def _getBrowserController(self):
        return self._proxy.getController(gc_constants.CONTROLLER.BROWSER)
