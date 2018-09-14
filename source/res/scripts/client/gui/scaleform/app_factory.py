# Embedded file name: scripts/client/gui/Scaleform/app_factory.py
import BattleReplay
from debug_utils import LOG_DEBUG
from gui import DialogsInterface, GUI_SETTINGS
from gui.Scaleform.LobbyEntry import LobbyEntry
from gui.Scaleform.Battle import Battle
from gui.Scaleform.LogitechMonitor import LogitechMonitor
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.settings import config as sf_config
from gui.Scaleform.framework.package_layout import PackageImporter
from gui.Scaleform.managers.Cursor import Cursor
from gui.Scaleform.managers.windows_stored_data import g_windowsStoredData
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.app_loader.interfaces import IAppFactory
from gui.app_loader.settings import APP_NAME_SPACE as _SPACE
from shared_utils import AlwaysValidObject

class NoAppFactory(AlwaysValidObject):

    def createLobby(self):
        LOG_DEBUG('NoAppFactory.createLobby')

    def destroyLobby(self):
        LOG_DEBUG('NoAppFactory.destroyLobby')

    def createBattle(self):
        LOG_DEBUG('NoAppFactory.createBattle')

    def destroyBattle(self):
        LOG_DEBUG('NoAppFactory.destroyBattle')


class AS3_AS2_AppFactory(IAppFactory):
    __slots__ = ('__apps', '__importer')

    def __init__(self):
        super(AS3_AS2_AppFactory, self).__init__()
        self.__apps = {_SPACE.SF_LOBBY: None,
         _SPACE.SF_BATTLE: None,
         _SPACE.SF_LOGITECH: None}
        self.__importer = PackageImporter()
        return

    def getPackageImporter(self):
        return self.__importer

    def hasApp(self, appNS):
        return appNS in self.__apps.keys()

    def getApp(self, appNS = None):
        app = None
        if appNS is not None:
            if appNS in self.__apps:
                app = self.__apps[appNS]
        else:
            app = self.__apps[_SPACE.SF_LOBBY]
            if not app:
                app = self.__apps[_SPACE.SF_BATTLE]
        return app

    def getDefLobbyApp(self):
        return self.__apps[_SPACE.SF_LOBBY]

    def getDefBattleApp(self):
        return self.__apps[_SPACE.SF_BATTLE]

    def createLobby(self):
        LOG_DEBUG('Creating app', _SPACE.SF_LOBBY)
        lobby = self.__apps[_SPACE.SF_LOBBY]
        if not lobby:
            lobby = LobbyEntry(_SPACE.SF_LOBBY)
            self.__importer.load(lobby.proxy, sf_config.COMMON_PACKAGES + sf_config.LOBBY_PACKAGES)
            self.__apps[_SPACE.SF_LOBBY] = lobby
        lobby.active(True)
        g_windowsStoredData.start()
        BattleReplay.g_replayCtrl.onCommonSwfLoaded()

    def destroyLobby(self):
        LOG_DEBUG('Destroying app', _SPACE.SF_LOBBY)
        if _SPACE.SF_LOBBY in self.__apps:
            lobby = self.__apps[_SPACE.SF_LOBBY]
            if lobby:
                lobby.close()
                self.__importer.unload(sf_config.LOBBY_PACKAGES)
                self.__apps[_SPACE.SF_LOBBY] = None
        g_windowsStoredData.stop()
        BattleReplay.g_replayCtrl.onCommonSwfUnloaded()
        return

    def showLobby(self):
        LOG_DEBUG('Shows lobby')
        self._setActive(_SPACE.SF_LOBBY, True)
        BattleReplay.g_replayCtrl.onCommonSwfLoaded()

    def hideLobby(self):
        LOG_DEBUG('Hides lobby')
        self._setActive(_SPACE.SF_LOBBY, False)
        BattleReplay.g_replayCtrl.onCommonSwfUnloaded()

    def createBattle(self):
        LOG_DEBUG('Creating app', _SPACE.SF_BATTLE)
        LogitechMonitor.onScreenChange('battle')
        battle = self.__apps[_SPACE.SF_BATTLE]
        if not battle:
            battle = self._getBattleAppInstance()
            self.__importer.load(battle.proxy, sf_config.COMMON_PACKAGES + sf_config.BATTLE_PACKAGES)
            self.__apps[_SPACE.SF_BATTLE] = battle
        BattleReplay.g_replayCtrl.onBattleSwfLoaded()
        battle.active(True)
        battle.component.visible = False

    def destroyBattle(self):
        LOG_DEBUG('Destroying app', _SPACE.SF_BATTLE)
        if _SPACE.SF_BATTLE in self.__apps:
            battle = self.__apps[_SPACE.SF_BATTLE]
            if battle:
                battle.close()
            self.__importer.unload(sf_config.BATTLE_PACKAGES)
            self.__apps[_SPACE.SF_BATTLE] = None
        return

    def attachCursor(self, appNS):
        if appNS not in self.__apps:
            return
        LOG_DEBUG('Attach cursor', appNS)
        app = self.__apps[appNS]
        if app and app.cursorMgr:
            app.cursorMgr.attachCursor(True)
        else:
            Cursor.setAutoShow(True)

    def detachCursor(self, appNS):
        if appNS not in self.__apps:
            return
        LOG_DEBUG('Detach cursor', appNS)
        app = self.__apps[appNS]
        if app and app.cursorMgr:
            app.cursorMgr.detachCursor(True)

    def destroy(self):
        for appNS in self.__apps.iterkeys():
            LOG_DEBUG('Destroying app', appNS)
            entry = self.__apps[appNS]
            if entry:
                entry.close()
            self.__apps[appNS] = None

        g_windowsStoredData.stop()
        if self.__importer is not None:
            self.__importer.unload()
            self.__importer = None
        return

    def goToIntroVideo(self, appNS):
        if appNS != _SPACE.SF_LOBBY:
            return
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.INTRO_VIDEO), EVENT_BUS_SCOPE.LOBBY)

    def goToLogin(self, appNS):
        if appNS != _SPACE.SF_LOBBY:
            return
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOGIN), EVENT_BUS_SCOPE.LOBBY)

    def goToLobby(self, appNS):
        if appNS != _SPACE.SF_LOBBY:
            return
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY), EVENT_BUS_SCOPE.LOBBY)

    def goToBattleLoading(self, appNS):
        if appNS != _SPACE.SF_LOBBY:
            return
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BATTLE_LOADING), EVENT_BUS_SCOPE.LOBBY)

    def goToTutorialLoading(self, appNS):
        if appNS != _SPACE.SF_LOBBY:
            return
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.TUTORIAL_LOADING), scope=EVENT_BUS_SCOPE.LOBBY)

    def goToFalloutMultiTeamLoading(self, appNS):
        if appNS != _SPACE.SF_LOBBY:
            return
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.FALLOUT_MULTI_TEAM_BATTLE_LOADING), scope=EVENT_BUS_SCOPE.LOBBY)

    def goToBattle(self, appNS):
        if appNS != _SPACE.SF_BATTLE:
            return
        battle = self.__apps[_SPACE.SF_BATTLE]
        if battle:
            self._loadBattlePage()
            battle.component.visible = True

    def showDisconnectDialog(self, appNS, description):
        if appNS == _SPACE.SF_LOBBY:
            DialogsInterface.showDisconnect(*description)

    def _getBattleAppInstance(self):
        return Battle(_SPACE.SF_BATTLE)

    def _loadBattlePage(self):
        pass

    def _setActive(self, appNS, isActive):
        app = self.__apps[appNS]
        if app:
            app.active(isActive)


def createAppFactory():
    if GUI_SETTINGS.isGuiEnabled():
        factory = AS3_AS2_AppFactory()
    else:
        factory = NoAppFactory()
    return factory
