# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/settings_core/battle_communications_settings.py
import typing
import BattleReplay
from Event import Event
from PlayerEvents import g_playerEvents
from account_helpers.settings_core.settings_constants import BattleCommStorageKeys
from helpers import dependency
from pve_battle_hud import WidgetType
from skeletons.account_helpers.settings_core import ISettingsCore, ISettingsCache, IBattleCommunicationsSettings
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.battle_communication import BattleCommunicationModel

class BattleCommunicationSettings(IBattleCommunicationsSettings):
    __slots__ = ('onChanged', '_isEnabled', '_showStickyMarkers', '_showInPlayerList', '_showCalloutMessages', '_showLocationMarkers', '_showBaseMarkers')
    _settingsCore = dependency.descriptor(ISettingsCore)
    _settingsCache = dependency.descriptor(ISettingsCache)
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleCommunicationSettings, self).__init__()
        self.onChanged = Event()
        self._isEnabled = None
        self._showStickyMarkers = None
        self._showInPlayerList = None
        self._showCalloutMessages = None
        self._showLocationMarkers = None
        self._showBaseMarkers = None
        return

    @property
    def isEnabled(self):
        return self._isEnabled

    @property
    def showStickyMarkers(self):
        return self._showStickyMarkers

    @property
    def showInPlayerList(self):
        return self._showInPlayerList

    @property
    def showCalloutMessages(self):
        return self._showCalloutMessages

    @property
    def showLocationMarkers(self):
        return self._showLocationMarkers

    @property
    def showBaseMarkers(self):
        return self._showBaseMarkers

    def init(self):
        self._settingsCore.onSettingsChanged += self._coreSettingsChangeHandler
        g_playerEvents.onAvatarBecomePlayer += self._avatarBecomePlayerHandler
        g_playerEvents.onAvatarBecomeNonPlayer += self._quitBattleHandler
        g_playerEvents.onDisconnected += self._quitBattleHandler
        if BattleReplay.g_replayCtrl.isPlaying:
            self._resolveEnabled()

    def fini(self):
        g_playerEvents.onAvatarBecomePlayer -= self._avatarBecomePlayerHandler
        g_playerEvents.onAvatarBecomeNonPlayer -= self._quitBattleHandler
        g_playerEvents.onDisconnected -= self._quitBattleHandler
        self._settingsCore.onSettingsChanged -= self._coreSettingsChangeHandler
        self._settingsCache.onSyncCompleted -= self._onSettingsReady

    def _quitBattleHandler(self):
        settingsCtrl = self._sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl:
            settingsCtrl.onSettingsChanged -= self._vseSettingsChangeHandler

    def _avatarBecomePlayerHandler(self):
        settingsCtrl = self._sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl:
            settingsCtrl.onSettingsChanged += self._vseSettingsChangeHandler
        if not self._settingsCache.settings.isSynced():
            self._settingsCache.onSyncCompleted += self._onSettingsReady
        else:
            self._resolveEnabled()

    def _onSettingsReady(self):
        self._settingsCache.onSyncCompleted -= self._onSettingsReady
        self._resolveEnabled()

    def _coreSettingsChangeHandler(self, _):
        self._resolveEnabled()

    def _vseSettingsChangeHandler(self, settingsID):
        if settingsID == WidgetType.BATTLE_COMMUNICATION:
            self._resolveEnabled()

    def _coreEnabled(self, name):
        return bool(self._settingsCore.getSetting(name))

    def _resolveEnabled(self):
        if not self._settingsCache.settings.isSynced() and not BattleReplay.g_replayCtrl.isPlaying:
            return
        vseEnabled = True
        settingsCtrl = self._sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl:
            settings = settingsCtrl.getSettings(WidgetType.BATTLE_COMMUNICATION)
            if settings:
                vseEnabled = not settings.hide
        isEnabled = self._coreEnabled(BattleCommStorageKeys.ENABLE_BATTLE_COMMUNICATION) and vseEnabled
        showStickyMarkers = self._coreEnabled(BattleCommStorageKeys.SHOW_STICKY_MARKERS) and vseEnabled
        showInPlayerList = self._coreEnabled(BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST) and vseEnabled
        showCalloutMessages = self._coreEnabled(BattleCommStorageKeys.SHOW_CALLOUT_MESSAGES) and vseEnabled
        showLocationMarkers = self._coreEnabled(BattleCommStorageKeys.SHOW_LOCATION_MARKERS) and vseEnabled
        showBaseMarkers = self._coreEnabled(BattleCommStorageKeys.SHOW_BASE_MARKERS) and vseEnabled
        if self._isEnabled != isEnabled or self._showStickyMarkers != showStickyMarkers or self._showInPlayerList != showInPlayerList or self._showCalloutMessages != showCalloutMessages or self._showLocationMarkers != showLocationMarkers or self._showBaseMarkers != showBaseMarkers:
            self._isEnabled = isEnabled
            self._showStickyMarkers = showStickyMarkers
            self._showInPlayerList = showInPlayerList
            self._showCalloutMessages = showCalloutMessages
            self._showLocationMarkers = showLocationMarkers
            self._showBaseMarkers = showBaseMarkers
            self.onChanged()
