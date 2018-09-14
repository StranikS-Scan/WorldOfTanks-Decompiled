# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/app_loader/interfaces.py
from gui import GUI_CTRL_MODE_FLAG as _CTRL_FLAG

class IAppFactory(object):

    def getPackageImporter(self):
        return None

    def hasApp(self, appNS):
        return False

    def getApp(self, appNS=None):
        return None

    def getDefLobbyApp(self):
        return None

    def getDefBattleApp(self):
        return None

    def createLobby(self):
        pass

    def destroyLobby(self):
        pass

    def showLobby(self):
        pass

    def hideLobby(self):
        pass

    def createBattle(self, arenaGuiType):
        pass

    def destroyBattle(self):
        pass

    def createLogitech(self):
        pass

    def destroy(self):
        pass

    def hasLobby(self):
        return False

    def hasBattle(self):
        return False

    def attachCursor(self, appNS, flags=_CTRL_FLAG.GUI_ENABLED):
        pass

    def detachCursor(self, appNS):
        pass

    def syncCursor(self, appNS, flags=_CTRL_FLAG.GUI_ENABLED):
        pass

    def goToIntroVideo(self, appNS):
        pass

    def goToLogin(self, appNS):
        pass

    def goToLobby(self, appNS):
        pass

    def goToBattleLoading(self, appNS, arenaGuiType):
        pass

    def goToBattle(self, appNS, arenaGuiType):
        pass

    def showDisconnectDialog(self, appNS, description):
        pass

    def handleKey(self, appNS, isDown, key, mods):
        return False
