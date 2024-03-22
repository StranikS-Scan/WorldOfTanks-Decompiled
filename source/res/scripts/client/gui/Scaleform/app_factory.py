# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/app_factory.py
import logging
import weakref
import BattleReplay
import BigWorld
from constants import ARENA_GUI_TYPE
from frameworks.wulf import WindowFlags
from gui import GUI_SETTINGS
from gui import GUI_CTRL_MODE_FLAG as _CTRL_FLAG
from gui.shared.system_factory import collectScaleformLobbyPackages, collectScaleformBattlePackages
from gui.Scaleform.battle_entry import BattleEntry
from gui.Scaleform.daapi.settings import config as sf_config
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS, VIEW_BATTLE_PAGE_ALIAS_BY_ARENA_GUI_TYPE
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.waiting_worker import WaitingWorker
from gui.Scaleform.framework.package_layout import PackageImporter
from gui.Scaleform.lobby_entry import LobbyEntry
from gui.Scaleform.managers.windows_stored_data import g_windowsStoredData
from gui.app_loader import settings as app_settings
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from shared_utils import AlwaysValidObject
from skeletons.gui.app_loader import IAppFactory
from skeletons.gui.impl import IGuiLoader
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())
_SPACE = app_settings.APP_NAME_SPACE

class EmptyAppFactory(AlwaysValidObject, IAppFactory):

    def __init__(self):
        super(EmptyAppFactory, self).__init__()
        self.__waiting = WaitingWorker()

    def createLobby(self):
        _logger.debug('EmptyAppFactory.createLobby')

    def destroyLobby(self):
        _logger.debug('EmptyAppFactory.destroyLobby')

    def reloadLobbyPackages(self):
        _logger.debug('EmptyAppFactory.reloadLobbyPackages')

    def createBattle(self, _):
        _logger.debug('EmptyAppFactory.createBattle')

    def destroyBattle(self):
        _logger.debug('EmptyAppFactory.destroyBattle')

    def getWaitingWorker(self):
        _logger.debug('EmptyAppFactory.getWaitingWorker')
        return self.__waiting


class AS3_AppFactory(IAppFactory):
    __slots__ = ('__apps', '__packages', '__importer', '__waiting', '__ctrlModeFlags', '__weakref__', '__gui')
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self):
        super(AS3_AppFactory, self).__init__()
        self.__apps = dict.fromkeys(_SPACE.RANGE)
        self.__packages = dict.fromkeys(_SPACE.RANGE)
        self.__importer = PackageImporter()
        self.__waiting = WaitingWorker()
        self.__waiting.start(weakref.proxy(self))
        self.__ctrlModeFlags = dict.fromkeys(_SPACE.RANGE, _CTRL_FLAG.CURSOR_DETACHED)

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

    def getWaitingWorker(self):
        return self.__waiting

    def createLobby(self):
        _logger.info('Creating app: %s', _SPACE.SF_LOBBY)
        lobby = self.__apps[_SPACE.SF_LOBBY]
        if lobby is None:
            lobby = LobbyEntry(_SPACE.SF_LOBBY, self.__ctrlModeFlags[_SPACE.SF_LOBBY])
            self.__apps[_SPACE.SF_LOBBY] = lobby
            lobbyPackages = tuple(collectScaleformLobbyPackages())
            self.__packages[_SPACE.SF_LOBBY] = lobbyPackages
            self.__importer.load(lobby.proxy, sf_config.COMMON_PACKAGES + lobbyPackages)
            self.__packages[_SPACE.SF_LOBBY] += tuple(g_overrideScaleFormViewsConfig.lobbyPackages)
            self.__importer.load(lobby.proxy, g_overrideScaleFormViewsConfig.lobbyPackages, None, True)
        lobby.active(True)
        g_windowsStoredData.start()
        return

    def reloadLobbyPackages(self):
        _logger.info('Reload app: %s', _SPACE.SF_LOBBY)
        lobby = self.__apps[_SPACE.SF_LOBBY]
        if lobby is not None:
            lobbyPackages = tuple(collectScaleformLobbyPackages())
            self.__importer.load(lobby.proxy, sf_config.COMMON_PACKAGES + lobbyPackages)
            self.__importer.load(lobby.proxy, g_overrideScaleFormViewsConfig.lobbyPackages, None, True)
        return

    def destroyLobby(self):
        if _SPACE.SF_LOBBY in self.__apps:
            lobby = self.__apps[_SPACE.SF_LOBBY]
            if lobby:
                _logger.info('Destroying app: %s', _SPACE.SF_LOBBY)
                lobby.close()
                self.__importer.unload(self.__packages[_SPACE.SF_LOBBY])
                self.__apps[_SPACE.SF_LOBBY] = None
                self.__ctrlModeFlags[_SPACE.SF_LOBBY] = _CTRL_FLAG.CURSOR_DETACHED
        g_windowsStoredData.stop()
        return

    def showLobby(self):
        _logger.debug('Shows lobby application')
        self._setActive(_SPACE.SF_LOBBY, True)
        BattleReplay.g_replayCtrl.disableTimeWarp()

    def hideLobby(self):
        _logger.debug('Hides lobby application')
        self._setActive(_SPACE.SF_LOBBY, False)

    def showBattle(self):
        _logger.debug('Shows battle application')
        self._setActive(_SPACE.SF_BATTLE, True)

    def hideBattle(self):
        _logger.debug('Hides battle application')
        self._setActive(_SPACE.SF_BATTLE, False)

    def createBattle(self, arenaGuiType):
        _logger.info('Creating app: %s', _SPACE.SF_BATTLE)
        battle = self.__apps[_SPACE.SF_BATTLE]
        if not battle:
            battle = BattleEntry(_SPACE.SF_BATTLE, self.__ctrlModeFlags[_SPACE.SF_BATTLE], arenaGuiType)
            self.__apps[_SPACE.SF_BATTLE] = battle
            packages = collectScaleformBattlePackages(arenaGuiType)
            if not packages:
                packages = sf_config.BATTLE_PACKAGES_BY_DEFAULT
            self.__packages[_SPACE.SF_BATTLE] = packages
            self.__importer.load(battle.proxy, sf_config.COMMON_PACKAGES + tuple(packages), arenaGuiType)
            packages = None
            if arenaGuiType in g_overrideScaleFormViewsConfig.battlePackages:
                packages = g_overrideScaleFormViewsConfig.battlePackages[arenaGuiType]
            if packages:
                self.__packages[_SPACE.SF_BATTLE] += tuple(packages)
                self.__importer.load(battle.proxy, packages, arenaGuiType, True)
        BattleReplay.g_replayCtrl.enableTimeWarp()
        BattleReplay.g_replayCtrl.onBattleLoadingFinished()
        BattleReplay.g_replayCtrl.loadServerSettings()
        battle.active(True)
        battle.setVisible(False)
        battle.detachCursor()
        return

    def destroyBattle(self):
        _logger.info('Destroying app: %s', _SPACE.SF_BATTLE)
        if _SPACE.SF_BATTLE in self.__apps:
            battle = self.__apps[_SPACE.SF_BATTLE]
            if battle:
                battle.close()
            seq = self.__packages[_SPACE.SF_BATTLE]
            if seq is not None:
                self.__importer.unload(seq)
            self.__apps[_SPACE.SF_BATTLE] = None
            self.__ctrlModeFlags[_SPACE.SF_BATTLE] = _CTRL_FLAG.CURSOR_DETACHED
        return

    def attachCursor(self, appNS, flags=_CTRL_FLAG.GUI_ENABLED):
        if appNS not in self.__apps:
            return
        else:
            _logger.debug('Attach cursor: %s', appNS)
            self.__ctrlModeFlags[appNS] = flags
            app = self.__apps[appNS]
            if app is not None:
                app.attachCursor(flags=flags)
            else:
                _logger.debug('Can not attach cursor because of app is not found: %s', appNS)
            return

    def detachCursor(self, appNS):
        if appNS not in self.__apps:
            return
        else:
            _logger.debug('Detach cursor: %s', appNS)
            self.__ctrlModeFlags[appNS] = _CTRL_FLAG.CURSOR_DETACHED
            app = self.__apps[appNS]
            if app is not None:
                app.detachCursor()
            else:
                _logger.debug('Can not detach cursor because of app is not found: %s', appNS)
            return

    def syncCursor(self, appNS, flags=_CTRL_FLAG.GUI_ENABLED):
        if appNS not in self.__apps:
            return
        else:
            _logger.debug('Sync cursor: %s', appNS)
            self.__ctrlModeFlags[appNS] = flags
            app = self.__apps[appNS]
            if app is not None:
                app.syncCursor(flags=flags)
            else:
                _logger.debug('Can not attach cursor because of app is not found: %s', appNS)
            return

    def destroy(self):
        for appNS in self.__apps.iterkeys():
            _logger.info('Destroying app: %s', appNS)
            entry = self.__apps[appNS]
            if entry:
                entry.close()
            self.__apps[appNS] = None

        if self.__waiting is not None:
            self.__waiting.stop()
            self.__waiting = None
        self.__packages = dict.fromkeys(_SPACE.RANGE)
        g_windowsStoredData.stop()
        if self.__importer is not None:
            self.__importer.unload()
            self.__importer = None
        return

    def goToLogin(self, appNS):
        if appNS != _SPACE.SF_LOBBY:
            return
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOGIN)), EVENT_BUS_SCOPE.LOBBY)

    def goToLobby(self, appNS):
        if appNS != _SPACE.SF_LOBBY:
            return
        app = self.getApp(appNS=appNS)
        libs = ['guiControlsLobbyBattleDynamic.swf',
         'guiControlsLobbyDynamic.swf',
         'guiControlsLobbyDynamic2.swf',
         'popovers.swf',
         'iconLibrary.swf']
        app.as_loadLibrariesS(libs)
        mainWindow = self.getMainWindow()
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY, parent=mainWindow)), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_VEHICLE_MARKER_VIEW, parent=mainWindow)), EVENT_BUS_SCOPE.LOBBY)

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
            BigWorld.player().logBattleLoadingFinished()
            self._toggleBattleLoading(False)

    def handleKey(self, appNS, isDown, key, mods):
        app = self.getApp(appNS=appNS)
        return app.handleKey(isDown, key, mods) if app is not None else False

    def _setActive(self, appNS, isActive):
        app = self.__apps[appNS]
        if app:
            app.setVisible(isActive)
            app.active(isActive)

    @classmethod
    def getMainWindow(cls):
        windows = cls.__gui.windowsManager.findWindows(lambda w: w.typeFlag == WindowFlags.MAIN_WINDOW)
        if not windows:
            _logger.error('The main window does not exist')
            return None
        else:
            return windows[0]

    @staticmethod
    def _loadBattlePage(arenaGuiType):
        viewAlias = VIEW_BATTLE_PAGE_ALIAS_BY_ARENA_GUI_TYPE.get(arenaGuiType, VIEW_ALIAS.CLASSIC_BATTLE_PAGE)
        event = events.LoadViewEvent(SFViewLoadParams(viewAlias, parent=AS3_AppFactory.getMainWindow()))
        g_eventBus.handleEvent(event, EVENT_BUS_SCOPE.BATTLE)

    @staticmethod
    def _toggleBattleLoading(toggle):
        event = events.GameEvent(events.GameEvent.BATTLE_LOADING, ctx={'isShown': toggle})
        g_eventBus.handleEvent(event, EVENT_BUS_SCOPE.BATTLE)


def createAppFactory(forceEmptyFactory=False):
    if GUI_SETTINGS.isGuiEnabled() and not forceEmptyFactory:
        factory = AS3_AppFactory()
    else:
        factory = EmptyAppFactory()
    return factory
