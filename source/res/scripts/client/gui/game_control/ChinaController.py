# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/ChinaController.py
from adisp import process
from gui.Scaleform.locale.MENU import MENU
from gui.game_control import gc_constants
from helpers import dependency
from skeletons.gui.game_control import IBrowserController, IChinaController, IGameSessionController

class NoChinaController(IChinaController):

    def showBrowser(self):
        pass


class ChinaController(IChinaController):
    gameSession = dependency.descriptor(IGameSessionController)
    browser = dependency.descriptor(IBrowserController)

    def __init__(self):
        super(ChinaController, self).__init__()
        self.__browserID = None
        return

    def onLobbyInited(self, event):
        if not self.gameSession.battlesCount % gc_constants.BROWSER.CHINA_BROWSER_COUNT:
            self.showBrowser()

    def onDisconnected(self):
        if self.__browserID is not None:
            self.__browserClosed(self.__browserID)
        return

    @process
    def showBrowser(self):
        self.__browserID = yield self.browser.load(title=MENU.BROWSER_WINDOW_TITLE, browserID=self.__browserID)
        self.browser.onBrowserDeleted += self.__browserClosed

    def __browserClosed(self, browserId):
        if browserId == self.__browserID:
            self.__browserID = None
            self.browser.onBrowserDeleted -= self.__browserClosed
        return
