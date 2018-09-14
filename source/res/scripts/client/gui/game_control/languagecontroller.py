# Embedded file name: scripts/client/gui/game_control/LanguageController.py
import BigWorld
from helpers import getClientLanguage
from gui.game_control.controllers import Controller

class LanguageController(Controller):

    def __init__(self, proxy):
        super(LanguageController, self).__init__(proxy)
        self.__currentLanguage = None
        return

    def onAccountBecomePlayer(self):
        if self.__currentLanguage is None:
            self.__currentLanguage = getClientLanguage()
            BigWorld.player().setLanguage(self.__currentLanguage)
        return

    def onDisconnected(self):
        self.__currentLanguage = None
        return
