# Embedded file name: scripts/client/gui/WindowsManager.py
import BigWorld
import Event
import constants
import BattleReplay
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.managers.windows_stored_data import g_windowsStoredData
from helpers import isShowStartupVideo
from gui.Scaleform.managers.Cursor import Cursor
from predefined_hosts import g_preDefinedHosts
from ConnectionManager import connectionManager
from constants import ARENA_GUI_TYPE
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_DEBUG
from gui import GUI_SETTINGS, game_control
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
from gui.shared.events import LoadViewEvent
from gui.Scaleform.LogitechMonitor import LogitechMonitor
from gui.Scaleform.AppEntry import AppEntry
from gui.Scaleform.Battle import Battle

class WindowsManager(object):

    def __init__(self):
        self.__window = None
        self.__battleWindow = None
        self.__em = Event.EventManager()
        self.__startVideoShown = False
        self.onInitBattleGUI = Event.Event(self.__em)
        self.onDestroyBattleGUI = Event.Event(self.__em)
        return

    @property
    def window(self):
        return self.__window

    @property
    def battleWindow(self):
        return self.__battleWindow

    def start(self):
        g_eventBus.addListener(events.GUICommonEvent.APP_STARTED, self.__onAppStarted)
        self.showLobby()

    def destroy(self):
        g_eventBus.removeListener(events.GUICommonEvent.APP_STARTED, self.__onAppStarted)
        self.hideAll()

    def onAccountShowGUI(self, ctx = None):
        if ctx is None:
            ctx = {}
        cursorMgr = self.window.cursorMgr
        if cursorMgr is not None:
            cursorMgr.attachCursor(True)
        else:
            Cursor.setAutoShow(True)
        if connectionManager.isConnected():
            self.window.fireEvent(LoadViewEvent(VIEW_ALIAS.LOBBY, ctx=ctx))
        else:
            LOG_WARNING('onAccountShowGUI: show lobby has been skipped, because client is not connected to server.')
        return

    def showStartGameVideo(self):
        if isShowStartupVideo():
            self.window.fireEvent(LoadViewEvent(VIEW_ALIAS.INTRO_VIDEO, ctx={'resultCallback': lambda *args: self.showLogin()}))
            return True
        return False

    def showLogin(self, callback = None):
        if self.window is not None:
            self.window.fireEvent(LoadViewEvent(VIEW_ALIAS.LOGIN, ctx={'callback': callback}))
        return

    def showLobby(self):
        if self.__window is None:
            self.__window = AppEntry()
        self.__window.active(True)
        g_windowsStoredData.start()
        BattleReplay.g_replayCtrl.onCommonSwfLoaded()
        return

    def hideLobby(self):
        if BattleReplay.isPlaying():
            self.__window.active(False)
        elif self.__window is not None:
            self.__window.close()
            self.__window = None
        g_windowsStoredData.stop()
        BattleReplay.g_replayCtrl.onCommonSwfUnloaded()
        return

    def startBattle(self):
        LogitechMonitor.onScreenChange('battle')
        self.__battleWindow = Battle()
        self.__battleWindow.active(True)
        self.__battleWindow.component.visible = False
        self.onInitBattleGUI()
        return self.__battleWindow

    def showBattle(self):
        self.hideLobby()
        if self.__battleWindow:
            self.__battleWindow.component.visible = True

    def destroyBattle(self):
        self.showLobby()
        self.__battleWindow.close()
        self.__battleWindow = None
        self.onDestroyBattleGUI()
        return

    def getHangarSpace(self):
        if not hasattr(self.__window, 'currentInterface') or not self.__window.currentInterface == 'hangar':
            return None
        else:
            return self.__window.space

    def hideAll(self):
        if self.__window is not None:
            self.__window.close()
            self.__window = None
        self.__battleWindow = None
        g_windowsStoredData.stop()
        return

    def showBattleLoading(self, isMultiTeam = False):
        if self.window.cursorMgr is not None:
            self.window.cursorMgr.detachCursor(True)
        g_preDefinedHosts.savePeripheryTL(connectionManager.peripheryID)
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None and arena.guiType is ARENA_GUI_TYPE.TUTORIAL:
            eventType = VIEW_ALIAS.TUTORIAL_LOADING
        elif isMultiTeam:
            eventType = VIEW_ALIAS.FALLOUT_MULTI_TEAM_BATTLE_LOADING
        else:
            eventType = VIEW_ALIAS.BATTLE_LOADING
        self.window.fireEvent(LoadViewEvent(eventType), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def showPostMortem(self):
        LogitechMonitor.onScreenChange('postmortem')
        if self.__battleWindow:
            self.__battleWindow.showPostmortemTips()

    def showBotsMenu(self):
        try:
            from gui.development.ui.BotsMenu import BotsMenu
            BotsMenu(self.__battleWindow).active(True)
        except ImportError:
            from debug_utils import LOG_ERROR
            LOG_ERROR('BotsMenu not found.')

    def __onAppStarted(self, event):
        if BattleReplay.g_replayCtrl.autoStartBattleReplay() or connectionManager.isConnected():
            return
        if not self.__startVideoShown:
            self.__startVideoShown = True
            if self.showStartGameVideo():
                return
        self.showLogin()


if GUI_SETTINGS.isGuiEnabled():
    g_windowsManager = WindowsManager()
else:
    from gui.development.no_gui.WindowsManager import WindowsManager
    g_windowsManager = WindowsManager()
