# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/WindowsManager.py
# Compiled at: 2018-11-29 14:33:44
import BigWorld
from ConnectionManager import connectionManager
from gui.Scaleform.CommonPage import CommonPage
from gui.Scaleform.Battle import Battle
from PlayerEvents import g_playerEvents
import Settings
from gui.Scaleform.LogitechMonitor import LogitechMonitor
from debug_utils import LOG_ERROR, LOG_DEBUG
from predefined_hosts import g_preDefinedHosts

class WindowsManager(object):

    def __init__(self):
        self.__window = None
        self.__battleWindow = None
        self._subscribe()
        self.__currentLanguage = None
        return

    def __getBattleWindow(self):
        return self.__battleWindow

    battleWindow = property(__getBattleWindow)

    def __getWindow(self):
        return self.__window

    def __setWindow(self, windowClass):
        if windowClass is None or not isinstance(self.__window, windowClass):
            if self.__window is not None:
                self.__window.close()
            self.__window = windowClass() if windowClass is not None else None
        return

    window = property(__getWindow, __setWindow)

    def _subscribe(self):
        g_playerEvents.onAccountShowGUI += self.showLobby
        g_playerEvents.onAccountBecomeNonPlayer += self.clearHangar
        g_playerEvents.onAvatarBecomePlayer += self.showBattleLoading

    def _unsubscribe(self):
        g_playerEvents.onAccountShowGUI -= self.showLobby
        g_playerEvents.onAccountBecomeNonPlayer -= self.clearHangar
        g_playerEvents.onAvatarBecomePlayer -= self.showBattleLoading

    def destroy(self):
        LogitechMonitor.destroy()
        self._unsubscribe()
        self.hideAll()

    def start(self):
        LogitechMonitor.init()
        prefs = Settings.g_instance.userPrefs
        if not prefs is None:
            showStartupMovie = prefs.readInt(Settings.KEY_SHOW_STARTUP_MOVIE, 1) == 1
            from BattleReplay import g_replayCtrl
            return g_replayCtrl.autoStartBattleReplay() and None
        else:
            if showStartupMovie:
                self.showStartGameVideo()
            else:
                self.showLogin()
            return

    def showStartGameVideo(self):
        self.window = CommonPage
        self.window.active(True)
        self.window.processStartGameVideo()

    def showLogin(self):
        self.__currentLanguage = None
        self.window = CommonPage
        self.window.active(True)
        self.window.processLogin()
        return

    def showLobby(self, ctx={}):
        if self.__currentLanguage is None:
            from helpers import getClientLanguage
            self.__currentLanguage = getClientLanguage()
            BigWorld.player().setLanguage(self.__currentLanguage)
        self.window = CommonPage
        self.window.active(True)
        self.window.processLobby(ctx.has_key('queueID'))
        return

    def getHangarSpace(self):
        if not hasattr(self.window, 'currentInterface') or not self.window.currentInterface == 'hangar':
            return None
        else:
            return self.window.space

    def hideAll(self):
        self.window = None
        self.clearHangar()
        return

    def clearHangar(self):
        from gui.Scaleform.utils.HangarSpace import g_hangarSpace
        g_hangarSpace.destroy()

    def showBattleLoading(self):
        g_preDefinedHosts.savePeripheryTL(connectionManager.peripheryID)
        BigWorld.wg_setReducedFpsMode(True)
        self.window = CommonPage
        self.window.active(True)
        self.window.processBattleLoading()

    def showBattle(self):
        if self.__window is not None and not isinstance(self.__window, Battle):
            self.__window.close()
            self.__window = None
        BigWorld.wg_setReducedFpsMode(False)
        if self.__battleWindow:
            self.__window = self.__battleWindow
            self.window.component.visible = True
        return

    def showPostMortem(self):
        LogitechMonitor.onScreenChange('postmortem')
        if self.__battleWindow:
            self.__battleWindow.showPostmortemTips()

    def startBattle(self):
        LogitechMonitor.onScreenChange('battle')
        self.__battleWindow = Battle()
        self.__battleWindow.active(True)
        self.__battleWindow.component.visible = False
        return self.__battleWindow

    def destroyBattle(self):
        self.__battleWindow.active(False)
        self.__battleWindow = None
        return

    def showBotsMenu(self):
        import exceptions
        try:
            from gui.Scaleform.development.BotsMenu import BotsMenu
            BotsMenu(self.__battleWindow).active(True)
        except exceptions.ImportError:
            from debug_utils import LOG_ERROR
            LOG_ERROR('Package gui.Scaleform.development not found.')


g_windowsManager = WindowsManager()
