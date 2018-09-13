# Embedded file name: scripts/client/gui/game_control/LanguageController.py
import BigWorld
from helpers import getClientLanguage

class LanguageController(object):

    def __init__(self):
        self.__currentLanguage = None
        return

    def init(self):
        pass

    def fini(self):
        pass

    def start(self):
        if self.__currentLanguage is None:
            self.__currentLanguage = getClientLanguage()
            BigWorld.player().setLanguage(self.__currentLanguage)
        return

    def stop(self):
        self.__currentLanguage = None
        return
