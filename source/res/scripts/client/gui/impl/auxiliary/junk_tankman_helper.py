# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/junk_tankman_helper.py
import BigWorld
import time
import Event
from constants import JUNK_CREW_CONVERSION_TOKEN
from gui.impl.lobby.crew.filter.data_providers import JunkTankmenDataProvider
from gui.ClientUpdateManager import g_clientUpdateManager
from skeletons.gui.shared import IItemsCache
from PlayerEvents import g_playerEvents
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

class JunkTankmanHelper(object):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        if self.initialized:
            return
        self.initialized = True
        self.noveltyMask = 0
        self.__isDisconnected = False
        self.isEnable = self.__lobbyContext.getServerSettings().isJunkCrewConversionEnabled()
        self.__userLogin = getattr(BigWorld.player(), 'name', '')
        self.onShowNoveltyUpdated = Event.Event()
        self.setIsConversionBannerVisible = Event.Event()
        self.__itemsCache.onSyncCompleted += self.__onCacheResync
        g_playerEvents.onDisconnected += self.__onDisconnected
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokenUpdate})
        self.__subscribe()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(JunkTankmanHelper, cls).__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def getJunkConversionToken(self):
        playerAccount = BigWorld.player()
        return playerAccount.tokens.getToken(JUNK_CREW_CONVERSION_TOKEN)

    def setAsShowed(self, showPlace):
        if self.noveltyMask & showPlace != showPlace:
            self.noveltyMask |= showPlace
            self.onShowNoveltyUpdated()

    def getTokenExpiration(self):
        token = self.getJunkConversionToken()
        timeLeft = 0
        if token:
            timeLeft = token[0] - int(time.time())
        return timeLeft

    def isShowNovelty(self, showPlace):
        return self.noveltyMask & showPlace != showPlace if self.isEnable and self.getJunkConversionToken() else None

    @property
    def canShowConversionBanner(self):
        return True if self.getJunkConversionToken() and self.isEnable else False

    @property
    def hasJunkTankmans(self):
        dataProvider = JunkTankmenDataProvider()
        dataProvider.update()
        return len(dataProvider.items()) > 0

    def __onTokenUpdate(self, diff):
        if JUNK_CREW_CONVERSION_TOKEN not in diff:
            return
        isVisible = bool(diff[JUNK_CREW_CONVERSION_TOKEN] and self.isEnable)
        self.noveltyMask = 0 if isVisible else 255
        self.setIsConversionBannerVisible(int(isVisible))
        self.onShowNoveltyUpdated()

    def __onServerSettingsChange(self, diff):
        isJunkCrewConversionEnabled = diff.get('isJunkCrewConversionEnabled')
        if isJunkCrewConversionEnabled is not None:
            self.isEnable = isJunkCrewConversionEnabled
            self.setIsConversionBannerVisible(int(isJunkCrewConversionEnabled))
            self.onShowNoveltyUpdated()
        return

    def __onCacheResync(self, reason, __):
        if reason == CACHE_SYNC_REASON.SHOW_GUI and self.__isDisconnected:
            self.__isDisconnected = False
            if self.__userLogin != getattr(BigWorld.player(), 'name', ''):
                self.isEnable = self.__lobbyContext.getServerSettings().isJunkCrewConversionEnabled()
                self.noveltyMask = 0
            self.__subscribe()

    def __onDisconnected(self):
        self.__isDisconnected = True

    def __subscribe(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
