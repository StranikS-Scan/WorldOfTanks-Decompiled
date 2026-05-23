# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/w2gt_controller.py
import logging
from collections import namedtuple
import typing
from BWUtil import AsyncReturn
import ArenaType
import BigWorld
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import GAME, GuiSettingsBehavior
from adisp import adisp_process
from client_request_lib.exceptions import ResponseCodes
from constants import Configs
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.wgcg.requests import WgcgRequestResponse
from gui.wgcg.w2gt.contexts import W2gtCtx
from helpers import dependency, server_settings, getClientVersion, time_utils
from helpers.caches.w2gt_cache import W2gtCache
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IW2GTGameController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
from wg_async import wg_async, await_callback
if typing.TYPE_CHECKING:
    from helpers.server_settings import _W2GTConfig
    from gui.battle_control.controllers.w2gt.w2gt_data_mgr import W2gtProgress
    from typing import Optional, Callable, Any, Dict
_logger = logging.getLogger(__name__)
_VALIDATE_RESPONSE_FIELDS = ('battle_zones',)
_ETAG_FIELD = 'etag'
_UPDATED_TIME_FIELD = 'Updated'
_NOT_MODIFIED_CODE = 304
_NEW_ACCOUNT_SESSIONS_COUNT = 2
_W2gtResponseData = namedtuple('_W2gtResponseData', ('success', 'responseCode', 'data'))

class W2GTGameController(IW2GTGameController):
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __webCtrl = dependency.descriptor(IWebController)

    def __init__(self):
        super(W2GTGameController, self).__init__()
        self.__w2gtConfig = None
        self.__isEnabledByPlayer = False
        self.__clientVersion = ''
        self.__cache = None
        return

    @property
    def isEnabled(self):
        return self.__isEnabledByPlayer and self.isEnabledByServer

    @property
    def isEnabledByServer(self):
        return self.__w2gtConfig is not None and self.__w2gtConfig.enabled

    @property
    def w2gtConfig(self):
        return self.__w2gtConfig

    def onConnected(self):
        self.__clientVersion = getClientVersion()
        self.__cache = W2gtCache()
        if self.__cache is not None:
            self.__cache.read()
        return

    def onDisconnected(self):
        self.__writeCache()
        self.__disposeCache()
        self.__clear()

    def onAccountBecomePlayer(self):
        self.__subscribe()

    def onLobbyInited(self, event):
        if self.__settingsCore.isReady:
            self.__applySettingsSection()
        else:
            self.__settingsCore.onSettingsReady += self.__onSettingsReady

    def saveProgress(self, arenaUniqueID, playerID, progress):
        self.__cache.saveProgress(arenaUniqueID, playerID, progress.asDict())

    def getProgress(self, arenaUniqueID, playerID):
        return self.__cache.getProgress(arenaUniqueID, playerID)

    @wg_async
    def getTips(self, geometryName, gameplayID, vehRole, vehLevel, team):
        if self.__isVehicleRestricted(vehRole, vehLevel):
            raise AsyncReturn(None)
        gameplayType = ArenaType.getGameplayName(gameplayID)
        cached = self.__getFromCache(geometryName, gameplayType, vehRole, vehLevel, team)
        cachedETag = cached.get(_ETAG_FIELD, '')
        updatedTime = cached.get(_UPDATED_TIME_FIELD, 0)
        data = None
        isSuccess = False
        responseCode = ResponseCodes.NO_ERRORS
        if cachedETag and self.__serverTime() - updatedTime < self.__w2gtConfig.dataLifetime:
            isSuccess = True
            data = cached
        else:
            key = self.__makeCacheKey(geometryName, gameplayType, vehRole, vehLevel, team)
            if self.__cache.isRequestSaved(key):
                cachedETag = None
            response = yield await_callback(self.__requestTips)(geometryName, gameplayType, vehRole, vehLevel, team, cachedETag)
            responseCode = response.getCode()
            if response.getExtraCode() == _NOT_MODIFIED_CODE:
                cached[_UPDATED_TIME_FIELD] = self.__serverTime()
                data = cached
                isSuccess = self.__validateResponse(data)
            elif response.isSuccess():
                self.__cache.saveRequest(key)
                eTag = response.getHeaderByKey(_ETAG_FIELD)
                data = response.getData() or {}
                isSuccess = self.__validateResponse(data)
                if isSuccess:
                    self.__addToCache(key, eTag, data)
            else:
                _logger.warning('Failed getting w2gt data. Code: %s.', responseCode)
        raise AsyncReturn(_W2gtResponseData(isSuccess, responseCode, data))
        return

    def __serverTime(self):
        return int(time_utils.getCurrentTimestamp())

    @adisp_process
    def __requestTips(self, geometryName, gameplayType, vehRole, vehLevel, team, eTag, callback):
        if self.__webCtrl.isAvailable():
            ctx = W2gtCtx(self.__clientVersion, eTag, geometryName, gameplayType, vehRole, vehLevel, team)
            response = yield self.__webCtrl.sendRequest(ctx=ctx)
            if not response.isSuccess():
                _logger.debug('W2GT service is unavailable. Data: %s.', response.getData())
                response = WgcgRequestResponse(ResponseCodes.W2GT_ERROR)
        else:
            response = WgcgRequestResponse(ResponseCodes.WGCG_ERROR)
            _logger.info('Web controller is unavailable')
        callback(response)

    def __validateResponse(self, data):
        for field in _VALIDATE_RESPONSE_FIELDS:
            if not data.get(field):
                _logger.debug('W2GT service: invalid data, field %s should not be empty. Data: %s.', field, data)
                return False

        return True

    def __subscribe(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onUpdateW2GTSettings
        self.__settingsCore.serverSettings.settingsCache.onSyncCompleted += self.__onServerSettingsSyncCompleted
        self.__updateConfig()

    def __unsubscribe(self):
        self.__settingsCore.serverSettings.settingsCache.onSyncCompleted -= self.__onServerSettingsSyncCompleted
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onUpdateW2GTSettings

    @server_settings.serverSettingsChangeListener(Configs.W2GT_CONFIG.value)
    def __onUpdateW2GTSettings(self, diff):
        self.__updateConfig()

    def __onSettingsReady(self):
        self.__applySettingsSection()
        self.__settingsCore.onSettingsReady -= self.__onSettingsReady

    def __applySettingsSection(self):
        isW2gtApplied = self.__settingsCore.serverSettings.getSectionSettings(SETTINGS_SECTIONS.GUI_START_BEHAVIOR, GuiSettingsBehavior.W2GT_APPLIED, 0)
        if not isW2gtApplied:
            isEnabledByPlayer = self.__isPlayerWinbacker() or self.__isNewPlayer()
            self.__settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.GUI_START_BEHAVIOR, {GuiSettingsBehavior.W2GT_APPLIED: True})
            self.__settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED_2, {GAME.W2GT_ENABLE: isEnabledByPlayer})
            g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdated)
            self.__isEnabledByPlayer = isEnabledByPlayer

    def __onServerSettingsSyncCompleted(self):
        self.__isEnabledByPlayer = bool(self.__settingsCore.getSetting(GAME.W2GT_ENABLE))

    def __onTokensUpdated(self, diff):
        if self.__lobbyContext.getServerSettings().winbackConfig.winbackAccessToken in diff:
            self.__settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED_2, {GAME.W2GT_ENABLE: True})
            g_clientUpdateManager.removeObjectCallbacks(self, force=True)

    def __isPlayerWinbacker(self):
        return self.__itemsCache.items.tokens.isTokenAvailable(self.__lobbyContext.getServerSettings().winbackConfig.winbackAccessToken)

    def __isVehicleRestricted(self, vehRole, vehLevel):
        if vehLevel in self.__w2gtConfig.restrictedVehicles:
            roles = self.__w2gtConfig.restrictedVehicles[vehLevel]
            return not roles or vehRole in roles
        return False

    def __clear(self):
        self.__unsubscribe()
        self.__w2gtConfig = None
        return

    def __updateConfig(self):
        self.__w2gtConfig = self.__lobbyContext.getServerSettings().w2gtConfig

    def __getFromCache(self, geometryName, gameplayType, vehRole, vehLevel, team):
        key = self.__makeCacheKey(geometryName, gameplayType, vehRole, vehLevel, team)
        return self.__cache.get(key, {})

    def __addToCache(self, key, eTag, data):
        data[_ETAG_FIELD] = eTag
        data[_UPDATED_TIME_FIELD] = self.__serverTime()
        self.__cache[key] = data

    def __makeCacheKey(self, *args):
        return '_'.join(map(str, args))

    def __disposeCache(self):
        if self.__cache:
            self.__cache.clear()
            self.__cache = None
        return

    def __writeCache(self):
        if self.__cache:
            self.__cache.write()

    @staticmethod
    def __isNewPlayer():
        return BigWorld.player().incarnationID < _NEW_ACCOUNT_SESSIONS_COUNT
