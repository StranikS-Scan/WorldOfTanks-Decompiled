# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/account_completion.py
import BigWorld
import constants
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import SHOW_DEMO_ACC_REGISTRATION
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from gui.platform.base.settings import CONTENT_WAITING
from gui.platform.base.statuses.constants import StatusTypes
from gui.platform.wgnp.steam_account.statuses import SteamAccEmailStatus
from gui.shared.event_dispatcher import showSteamAddEmailOverlay, showSteamConfirmEmailOverlay
from gui.shared.lock_overlays import lockNotificationManager
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IOverlayController, ISteamCompletionController, IDemoAccCompletionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.login_manager import ILoginManager
from skeletons.gui.platform.wgnp_controllers import IWGNPSteamAccRequestController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from wg_async import wg_async, wg_await

class SteamCompletionController(ISteamCompletionController):
    _loginManager = dependency.descriptor(ILoginManager)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _wgnpSteamAccCtrl = dependency.descriptor(IWGNPSteamAccRequestController)
    _overlayController = dependency.descriptor(IOverlayController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __connectionManager = dependency.descriptor(IConnectionManager)

    def __init__(self):
        super(SteamCompletionController, self).__init__()
        self.__isLobbyInited = False

    @property
    def isSteamAccount(self):
        return self._loginManager.isWgcSteam

    @property
    def isAddEmailOverlayShown(self):
        uiStorage = self.__settingsCore.serverSettings.getUIStorage2()
        return uiStorage.get(UI_STORAGE_KEYS.STEAM_ADD_EMAIL_OVERLAY_SHOWN)

    @property
    def isConfirmEmailOverlayAllowed(self):
        uiStorage = self.__settingsCore.serverSettings.getUIStorage2()
        return uiStorage.get(UI_STORAGE_KEYS.IS_CONFIRM_EMAIL_OVERLAY_ALLOWED)

    def onLobbyStarted(self, ctx):
        if not self.__isLobbyInited:
            lockNotificationManager(lock=True)

    def onLobbyInited(self, event):
        if self.__isLobbyInited:
            return
        self.__subscribe()
        self.__isLobbyInited = True

    def onAvatarBecomePlayer(self):
        avatar = BigWorld.player()
        if avatar is not None:
            if avatar.arenaGuiType in constants.ARENA_GUI_TYPE.RANDOM_RANGE:
                self.__unsubscribe()
                self.__isLobbyInited = True
        return

    def onDisconnected(self):
        self.__clear()

    def __subscribe(self):
        self._hangarSpace.onSpaceCreate += self.__onSpaceCreate

    def __unsubscribe(self):
        self._hangarSpace.onSpaceCreate -= self.__onSpaceCreate

    def __clear(self):
        self.__unsubscribe()
        self.__isLobbyInited = False

    @wg_async
    def __onSpaceCreate(self):
        self.__unsubscribe()
        if self._overlayController.isActive or not self.isSteamAccount or not self.__canSteamShadeShow():
            lockNotificationManager(lock=False, releasePostponed=True)
            return
        status = yield wg_await(self._wgnpSteamAccCtrl.getEmailStatus(waitingID=CONTENT_WAITING))
        if status.isUndefined or not self._hangarSpace.spaceInited:
            lockNotificationManager(lock=False, releasePostponed=True)
            return
        if status.typeIs(StatusTypes.ADD_NEEDED) and not self.isAddEmailOverlayShown:
            showSteamAddEmailOverlay()
            lockNotificationManager(lock=False, releasePostponed=True, fireReleased=False)
        elif status.typeIs(StatusTypes.ADDED) and self.isConfirmEmailOverlayAllowed:
            showSteamConfirmEmailOverlay(email=status.email)
        lockNotificationManager(lock=False, releasePostponed=True)

    def __canSteamShadeShow(self):
        steamShadeConfig = self._lobbyContext.getServerSettings().steamShadeConfig
        if steamShadeConfig.battlesPlayed < 0 and steamShadeConfig.sessions < 0:
            return False
        battles = self._itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount()
        sessions = BigWorld.player().incarnationID
        sessions = sessions if self.__connectionManager.isStandalone() else sessions / 2
        return steamShadeConfig.battlesPlayed <= battles and steamShadeConfig.sessions < sessions

    def setAddEmailOverlayShown(self):
        self.__settingsCore.serverSettings.saveInUIStorage2({UI_STORAGE_KEYS.STEAM_ADD_EMAIL_OVERLAY_SHOWN: True})

    def setConfirmEmailOverlayAllowed(self, isAllowed):
        self.__settingsCore.serverSettings.saveInUIStorage2({UI_STORAGE_KEYS.IS_CONFIRM_EMAIL_OVERLAY_ALLOWED: isAllowed})


class DemoAccCompletionController(IDemoAccCompletionController):

    def __init__(self):
        super(DemoAccCompletionController, self).__init__()
        self._isDemoAccount = False
        self._isDemoAccountOnce = False
        self._controllerDestroyed = False

    def init(self):
        g_playerEvents.onClientUpdated += self._onClientUpdate

    def fini(self):
        g_playerEvents.onClientUpdated -= self._onClientUpdate
        self._controllerDestroyed = True

    def onDisconnected(self):
        self._isDemoAccount = False
        self._isDemoAccountOnce = False

    @property
    def isDemoAccount(self):
        return self._isDemoAccount

    @property
    def isDemoAccountOnce(self):
        return self._isDemoAccountOnce

    @property
    def isInDemoAccRegistration(self):
        needShow = AccountSettings.getSettings(SHOW_DEMO_ACC_REGISTRATION)
        return self.isDemoAccount and needShow

    @isInDemoAccRegistration.setter
    def isInDemoAccRegistration(self, value):
        AccountSettings.setSettings(SHOW_DEMO_ACC_REGISTRATION, value)

    def _onClientUpdate(self, diff, _):
        if constants.DEMO_ACCOUNT_ATTR in diff:
            self._isDemoAccount = bool(diff.get(constants.DEMO_ACCOUNT_ATTR))
            self._isDemoAccountOnce = self._isDemoAccountOnce or self._isDemoAccount
