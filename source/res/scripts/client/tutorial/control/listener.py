# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/listener.py
from gui import GUI_SETTINGS
from gui.app_loader import g_appLoader, settings
from tutorial.settings import TUTORIAL_SETTINGS
_SPACE_ID = settings.GUI_GLOBAL_SPACE_ID

class AppLoaderListener(object):

    def __init__(self):
        super(AppLoaderListener, self).__init__()
        self.__loader = None
        return

    def start(self, loader):
        self.__loader = loader
        g_appLoader.onGUISpaceEntered += self.__onGUISpaceEntered
        g_appLoader.onGUISpaceLeft += self.__onGUISpaceLeft

    def stop(self):
        g_appLoader.onGUISpaceEntered -= self.__onGUISpaceEntered
        g_appLoader.onGUISpaceLeft -= self.__onGUISpaceLeft

    def __onGUISpaceEntered(self, spaceID):
        if spaceID == _SPACE_ID.LOGIN:
            self.__loader.goToLogin()
        elif spaceID == _SPACE_ID.LOBBY:
            self.__loader.goToLobby()
        elif spaceID == _SPACE_ID.BATTLE:
            if GUI_SETTINGS.useAS3Battle:
                battleSettings = TUTORIAL_SETTINGS.BATTLE_V2
            else:
                battleSettings = TUTORIAL_SETTINGS.BATTLE
            self.__loader.goToBattle(battleSettings=battleSettings)

    def __onGUISpaceLeft(self, spaceID):
        if spaceID == _SPACE_ID.LOBBY:
            self.__loader.leaveLobby()
        elif spaceID == _SPACE_ID.BATTLE:
            self.__loader.leaveBattle()
