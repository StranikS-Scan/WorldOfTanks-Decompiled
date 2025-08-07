# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_anniversary_controller.py
import logging
import datetime
import typing
from Event import EventManager, Event
from constants import Configs
from gui.impl.lobby.wot_anniversary.bonuses_layout_manager import BonusesLayoutManager
from gui.impl.lobby.wot_anniversary.content_loader.cache import WotAnniversaryCdnCacheMgr
from gui.impl.lobby.wot_anniversary.wot_anniversary_helpers import showWelcomeScreen
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, server_settings, time_utils
from skeletons.gui.game_control import IHangarLoadingController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.wot_anniversary import IWotAnniversaryController
if typing.TYPE_CHECKING:
    from helpers.server_settings import WotAnniversaryConfig
_logger = logging.getLogger(__name__)

class WotAnniversaryController(IWotAnniversaryController):
    __hangarLoadingController = dependency.descriptor(IHangarLoadingController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(WotAnniversaryController, self).__init__()
        self.__bonusLayoutManager = None
        self.__em = EventManager()
        self.onSettingsChanged = Event(self.__em)
        self.onNextEnvelopeArrived = Event(self.__em)
        self.onStartDateReached = Event(self.__em)
        self.onEndDateReached = Event(self.__em)
        self.__nextActionNotifier = SimpleNotifier(self.__getTimeToNextAction, self.__onNotifyNextAction)
        self.__cdnCacheMgr = WotAnniversaryCdnCacheMgr()
        return

    @property
    def config(self):
        return self.__lobbyContext.getServerSettings().wotAnniversaryConfig

    @property
    def cdnCacheMgr(self):
        return self.__cdnCacheMgr

    @property
    def bonusLayoutManager(self):
        return self.__bonusLayoutManager

    def init(self):
        super(WotAnniversaryController, self).init()
        self.__bonusLayoutManager = BonusesLayoutManager()
        self.__bonusLayoutManager.init()

    def fini(self):
        super(WotAnniversaryController, self).fini()
        self.__clear()
        self.__bonusLayoutManager.fini()
        self.__bonusLayoutManager = None
        self.__nextActionNotifier.clear()
        self.__nextActionNotifier = None
        return

    def onLobbyInited(self, event):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__nextActionNotifier.startNotification()
        if not self.isEnabled():
            return
        self.__cdnCacheMgr.startSync()

    def onAccountBecomeNonPlayer(self):
        self.__clear()

    def onConnected(self):
        self.__hangarLoadingController.onHangarLoadedAfterLogin += self.__onHangarLoadedAfterLogin

    def onDisconnected(self):
        self.__clear()

    def isEnabled(self):
        now = time_utils.getServerUTCTime()
        return self.config.isEnabled and self.config.startDate <= now <= self.config.endDate

    def getReleasedEnvelopCount(self):
        return 0 if not self.isEnabled() else (time_utils.getServerUTCTime() - self.config.startDate) // time_utils.ONE_DAY + 1

    def getAvailableEnvelops(self):
        return min(max(0, self.getReleasedEnvelopCount() - self.getDayTokenCount()), len(self.config.days))

    def getDayTokenCount(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.config.dayToken)

    def getProgressionTokenCount(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.config.progressionToken)

    def __getTimeToNextAction(self):
        now = time_utils.getServerUTCTime()
        if not self.config.isEnabled or now > self.config.endDate:
            return 0
        return self.config.startDate - now if now < self.config.startDate else min(time_utils.ONE_DAY - datetime.timedelta(seconds=now - self.config.startDate).seconds, self.config.endDate - now)

    def __onNotifyNextAction(self):
        now = time_utils.getServerUTCTime()
        if now >= self.config.endDate:
            self.onEndDateReached()
        elif self.config.startDate + time_utils.ONE_DAY >= now:
            self.onStartDateReached()
            showWelcomeScreen()
            self.__cdnCacheMgr.startSync()
        else:
            self.__cdnCacheMgr.reload()
            self.onNextEnvelopeArrived()

    @server_settings.serverSettingsChangeListener(Configs.WOT_ANNIVERSARY_CONFIG.value)
    def __onServerSettingsChanged(self, _):
        self.onSettingsChanged()
        self.__nextActionNotifier.startNotification()
        if self.isEnabled():
            self.__cdnCacheMgr.startSync()

    def __onHangarLoadedAfterLogin(self):
        showWelcomeScreen()

    def __clear(self):
        self.__hangarLoadingController.onHangarLoadedAfterLogin -= self.__onHangarLoadedAfterLogin
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__em.clear()
        self.__cdnCacheMgr.stopSync()
        self.__nextActionNotifier.stopNotification()
