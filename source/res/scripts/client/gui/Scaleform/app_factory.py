# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/app_factory.py
import BattleReplay
from constants import ARENA_GUI_TYPE
from debug_utils import LOG_DEBUG
from gui import DialogsInterface, GUI_SETTINGS
from gui import GUI_CTRL_MODE_FLAG as _CTRL_FLAG
from gui.Scaleform.battle_entry import BattleEntry
from gui.Scaleform.lobby_entry import LobbyEntry
from gui.Scaleform.daapi.settings import config as sf_config
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.package_layout import PackageImporter
from gui.Scaleform.managers.windows_stored_data import g_windowsStoredData
from gui.app_loader.interfaces import IAppFactory
from gui.app_loader.settings import APP_NAME_SPACE as _SPACE
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from shared_utils import AlwaysValidObject

class NoAppFactory(AlwaysValidObject, IAppFactory):

    def createLobby(self):
        LOG_DEBUG('NoAppFactory.createLobby')

    def destroyLobby(self):
        LOG_DEBUG('NoAppFactory.destroyLobby')

    def reloadLobbyPackages(self):
        LOG_DEBUG('NoAppFactory.reloadLobbyPackages')

    def createBattle(self, _):
        LOG_DEBUG('NoAppFactory.createBattle')

    def destroyBattle(self):
        LOG_DEBUG('NoAppFactory.destroyBattle')


class AS3_AppFactory(IAppFactory):
    __slots__ = ('__apps', '__packages', '__importer')

    def __init__(self):
        super(AS3_AppFactory, self).__init__()
        self.__apps = dict.fromkeys(_SPACE.RANGE)
        self.__packages = dict.fromkeys(_SPACE.RANGE)
        self.__importer = PackageImporter()

    def getPackageImporter(self):
        return self.__importer

    def hasApp(self, appNS):
        return appNS in self.__apps.keys()

    def getApp(self, appNS=None):
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
        if lobby is None:
            lobby = LobbyEntry(_SPACE.SF_LOBBY)
            self.__packages[_SPACE.SF_LOBBY] = sf_config.LOBBY_PACKAGES
            self.__importer.load(lobby.proxy, sf_config.COMMON_PACKAGES + self.__packages[_SPACE.SF_LOBBY])
            self.__apps[_SPACE.SF_LOBBY] = lobby
        lobby.active(True)
        g_windowsStoredData.start()
        return

    def reloadLobbyPackages(self):
        LOG_DEBUG('Reload app', _SPACE.SF_LOBBY)
        lobby = self.__apps[_SPACE.SF_LOBBY]
        if lobby is not None:
            self.__importer.load(lobby.proxy, sf_config.COMMON_PACKAGES + sf_config.LOBBY_PACKAGES)
        return

    def destroyLobby(self):
        LOG_DEBUG('Destroying app', _SPACE.SF_LOBBY)
        if _SPACE.SF_LOBBY in self.__apps:
            lobby = self.__apps[_SPACE.SF_LOBBY]
            if lobby:
                lobby.close()
                self.__importer.unload(self.__packages[_SPACE.SF_LOBBY])
                self.__apps[_SPACE.SF_LOBBY] = None
        g_windowsStoredData.stop()
        return

    def showLobby(self):
        LOG_DEBUG('Shows lobby application')
        self._setActive(_SPACE.SF_LOBBY, True)
        BattleReplay.g_replayCtrl.onCommonSwfLoaded()

    def hideLobby(self):
        LOG_DEBUG('Hides lobby application')
        self._setActive(_SPACE.SF_LOBBY, False)

    def showBattle(self):
        LOG_DEBUG('Shows battle application')
        self._setActive(_SPACE.SF_BATTLE, True)

    def hideBattle(self):
        LOG_DEBUG('Hides battle application')
        self._setActive(_SPACE.SF_BATTLE, False)

    def createBattle(self, arenaGuiType):
        LOG_DEBUG('Creating app', _SPACE.SF_BATTLE)
        battle = self.__apps[_SPACE.SF_BATTLE]
        if not battle:
            battle = BattleEntry(_SPACE.SF_BATTLE)
            packages = sf_config.BATTLE_PACKAGES
            if arenaGuiType in sf_config.BATTLE_PACKAGES_BY_ARENA_TYPE:
                packages += sf_config.BATTLE_PACKAGES_BY_ARENA_TYPE[arenaGuiType]
            else:
                packages += sf_config.BATTLE_PACKAGES_BY_DEFAULT
            self.__packages[_SPACE.SF_BATTLE] = packages
            self.__importer.load(battle.proxy, sf_config.COMMON_PACKAGES + packages)
            self.__apps[_SPACE.SF_BATTLE] = battle
        BattleReplay.g_replayCtrl.onBattleSwfLoaded()
        battle.active(True)
        battle.component.visible = False
        battle.detachCursor()

    def destroyBattle(self):
        LOG_DEBUG('Destroying app', _SPACE.SF_BATTLE)
        if _SPACE.SF_BATTLE in self.__apps:
            battle = self.__apps[_SPACE.SF_BATTLE]
            if battle:
                battle.close()
            self.__importer.unload(self.__packages[_SPACE.SF_BATTLE])
            self.__apps[_SPACE.SF_BATTLE] = None
        return

    def attachCursor(self, appNS, flags=_CTRL_FLAG.GUI_ENABLED):
        if appNS not in self.__apps:
            return
        else:
            LOG_DEBUG('Attach cursor', appNS)
            app = self.__apps[appNS]
            if app is not None:
                app.attachCursor(flags=flags)
            else:
                LOG_DEBUG('Can not attach cursor because of app is not found', appNS)
            return

    def detachCursor(self, appNS):
        if appNS not in self.__apps:
            return
        else:
            LOG_DEBUG('Detach cursor', appNS)
            app = self.__apps[appNS]
            if app is not None:
                app.detachCursor()
            else:
                LOG_DEBUG('Can not detach cursor because of app is not found', appNS)
            return

    def syncCursor(self, appNS, flags=_CTRL_FLAG.GUI_ENABLED):
        if appNS not in self.__apps:
            return
        else:
            LOG_DEBUG('Attach cursor', appNS)
            app = self.__apps[appNS]
            if app is not None:
                app.syncCursor(flags=flags)
            else:
                LOG_DEBUG('Can not attach cursor because of app is not found', appNS)
            return

    def destroy(self):
        for appNS in self.__apps.iterkeys():
            LOG_DEBUG('Destroying app', appNS)
            entry = self.__apps[appNS]
            if entry:
                entry.close()
            self.__apps[appNS] = None

        self.__packages = dict.fromkeys(_SPACE.RANGE)
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

    def loadBattlePage(self, appNS, arenaGuiType=ARENA_GUI_TYPE.UNKNOWN):
        if appNS != _SPACE.SF_BATTLE:
            return
        else:
            battle = self.__apps[_SPACE.SF_BATTLE]
            if battle is not None:
                self._loadBattlePage(arenaGuiType)
            return

    def goToBattleLoading(self, appNS):
        if appNS != _SPACE.SF_BATTLE:
            return
        else:
            battle = self.__apps[_SPACE.SF_BATTLE]
            if battle is not None:
                self._toggleBattleLoading(True)
            return

    def goToBattlePage(self, appNS):
        if appNS != _SPACE.SF_BATTLE:
            return
        battle = self.__apps[_SPACE.SF_BATTLE]
        if battle:
            self._toggleBattleLoading(False)

    def showDisconnectDialog(self, appNS, description):
        if appNS == _SPACE.SF_LOBBY:
            DialogsInterface.showDisconnect(*description)

    def handleKey(self, appNS, isDown, key, mods):
        app = self.getApp(appNS=appNS)
        if app is not None:
            return app.handleKey(isDown, key, mods)
        else:
            return False
            return

    def _setActive(self, appNS, isActive):
        app = self.__apps[appNS]
        if app:
            app.component.visible = isActive
            app.active(isActive)

    @staticmethod
    def _loadBattlePage(arenaGuiType):
        if arenaGuiType == ARENA_GUI_TYPE.TUTORIAL:
            event = events.LoadViewEvent(VIEW_ALIAS.TUTORIAL_BATTLE_PAGE)
        elif arenaGuiType == ARENA_GUI_TYPE.FALLOUT_CLASSIC:
            event = events.LoadViewEvent(VIEW_ALIAS.FALLOUT_CLASSIC_PAGE)
        elif arenaGuiType in (ARENA_GUI_TYPE.EPIC_RANDOM, ARENA_GUI_TYPE.EPIC_RANDOM_TRAINING):
            event = events.LoadViewEvent(VIEW_ALIAS.EPIC_RANDOM_PAGE)
        elif arenaGuiType == ARENA_GUI_TYPE.FALLOUT_MULTITEAM:
            event = events.LoadViewEvent(VIEW_ALIAS.FALLOUT_MULTITEAM_PAGE)
        elif arenaGuiType == ARENA_GUI_TYPE.RANKED:
            event = events.LoadViewEvent(VIEW_ALIAS.RANKED_BATTLE_PAGE)
        elif arenaGuiType == ARENA_GUI_TYPE.BOOTCAMP:
            event = events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_BATTLE_PAGE)
        else:
            event = events.LoadViewEvent(VIEW_ALIAS.CLASSIC_BATTLE_PAGE)
        g_eventBus.handleEvent(event, EVENT_BUS_SCOPE.BATTLE)

    @staticmethod
    def _toggleBattleLoading(toggle):
        event = events.GameEvent(events.GameEvent.BATTLE_LOADING, ctx={'isShown': toggle})
        g_eventBus.handleEvent(event, EVENT_BUS_SCOPE.BATTLE)


def createAppFactory():
    if GUI_SETTINGS.isGuiEnabled():
        factory = AS3_AppFactory()
    else:
        factory = NoAppFactory()
    return factory
