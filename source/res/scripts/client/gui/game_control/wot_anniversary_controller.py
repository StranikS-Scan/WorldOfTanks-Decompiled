# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_anniversary_controller.py
import logging
import re
import typing
from Event import EventManager, Event
from account_helpers.AccountSettings import WOT_ANNIVERSARY_SEEN_EVENT_WILL_END_SOON_NOTIFICATION
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import WotAnniversaryStorageKeys
from gui.shared.utils.scheduled_notifications import AcyclicNotifier
from gui.wot_anniversary.wot_anniversary_helpers import showWotAnniversaryWelcomeWindow, WOT_ANNIVERSARY_DAILY_QUEST_PREFIX, WOT_ANNIVERSARY_PREFIX, WOT_ANNIVERSARY_DAILY_TOKEN_PREFIX, WotAnniversaryEventState, getWotAnniversarySectionSetting, setWotAnniversarySectionSetting
from helpers import dependency, time_utils
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IWotAnniversaryController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from wot_anniversary_common import WOT_ANNIVERSARY_CONFIG_NAME
if typing.TYPE_CHECKING:
    from helpers.server_settings import _WotAnniversaryConfig
_logger = logging.getLogger(__name__)

class WotAnniversaryController(IWotAnniversaryController):
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(WotAnniversaryController, self).__init__()
        self.__em = EventManager()
        self.onSettingsChanged = Event(self.__em)
        self.onEventWillEndSoon = Event(self.__em)
        self.onEventStateChanged = Event(self.__em)
        self.__isEnabled = None
        self.__isAvailable = None
        self.__eventWillEndSoonNotifier = AcyclicNotifier(self.__getTimeTillEventWillEndSoonNotification, self.__notifyEventWillEndSoon)
        self.__dailyQuestPattern = re.compile('^{0}\\d+$'.format(WOT_ANNIVERSARY_DAILY_TOKEN_PREFIX))
        return

    def onLobbyInited(self, event):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__startEventWillEndSoonNotification()
        self.__showWotAnniversaryWelcomeWindow()
        self.__updateLastEventState()

    def onAccountBecomeNonPlayer(self):
        self.__clear()

    def fini(self):
        self.__clear()
        self.__dailyQuestPattern = None
        self.__eventWillEndSoonNotifier.clear()
        if self.__eventWillEndSoonNotifier is not None:
            self.__eventWillEndSoonNotifier = None
        return

    def onDisconnected(self):
        self.__clear()

    def isEnabled(self):
        return self.getConfig().isEnabled

    def isAvailable(self):
        return self.isEnabled() and self.getConfig().isActive

    def getConfig(self):
        return self.__lobbyContext.getServerSettings().wotAnniversaryConfig

    def getQuests(self):
        return self.__eventsCache.getHiddenQuests(self.__filterFunc)

    def getDailyQuestName(self):
        allTokens = set(self.__itemsCache.items.tokens.getTokens().keys())
        dqToken = findFirst(lambda tID: self.__dailyQuestPattern.match(tID) is not None, allTokens, '')
        questID = dqToken.split(':')[-1]
        return WOT_ANNIVERSARY_DAILY_QUEST_PREFIX + questID if questID.isdigit() else None

    def isLastDayNow(self):
        return time_utils.getCurrentLocalServerTimestamp() + time_utils.ONE_DAY >= self.getConfig().endTime

    def getUrl(self, urlName):
        return self.getConfig().anniversaryUrls.get(urlName, '')

    def __onServerSettingsChanged(self, diff):
        if WOT_ANNIVERSARY_CONFIG_NAME in diff:
            self.onSettingsChanged()
            self.__startEventWillEndSoonNotification()
            self.__showWotAnniversaryWelcomeWindow()
            self.__updateLastEventState()

    def __clear(self):
        self.__eventWillEndSoonNotifier.stopNotification()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__em.clear()

    @classmethod
    def __filterFunc(cls, quest):
        return quest.getID().startswith(WOT_ANNIVERSARY_PREFIX)

    def __startEventWillEndSoonNotification(self):
        if self.isAvailable() and not getWotAnniversarySectionSetting(WOT_ANNIVERSARY_SEEN_EVENT_WILL_END_SOON_NOTIFICATION) and self.__eventWillEndSoonNotifier is not None:
            self.__eventWillEndSoonNotifier.startNotification()
        return

    def __showWotAnniversaryWelcomeWindow(self):
        if self.isAvailable() and not self.__settingsCore.serverSettings.getSection(SETTINGS_SECTIONS.WOT_ANNIVERSARY_STORAGE).get(WotAnniversaryStorageKeys.WOT_ANNIVERSARY_WELCOME_SHOWED):
            showWotAnniversaryWelcomeWindow(useQueue=True)

    def __getTimeTillEventWillEndSoonNotification(self):
        endTime = self.getConfig().endTime
        timeTillEventWillEndSoon = time_utils.getCurrentLocalServerTimestamp() + time_utils.ONE_DAY * 3
        return max(endTime - timeTillEventWillEndSoon, 1)

    def __notifyEventWillEndSoon(self):
        if self.isAvailable() and not getWotAnniversarySectionSetting(WOT_ANNIVERSARY_SEEN_EVENT_WILL_END_SOON_NOTIFICATION) and self.__eventWillEndSoonNotifier is not None:
            setWotAnniversarySectionSetting(WOT_ANNIVERSARY_SEEN_EVENT_WILL_END_SOON_NOTIFICATION, True)
            self.onEventWillEndSoon()
        return

    def __updateLastEventState(self):
        isEnabled = self.isEnabled()
        isAvailable = self.isAvailable()
        if isEnabled and self.__isAvailable != isAvailable:
            if not isAvailable:
                self.onEventStateChanged(WotAnniversaryEventState.PAUSE)
            elif self.__isEnabled:
                self.onEventStateChanged(WotAnniversaryEventState.ENABLED)
        elif self.__isEnabled and self.__isEnabled != isEnabled:
            self.onEventStateChanged(WotAnniversaryEventState.FINISHED)
        self.__isEnabled = isEnabled
        self.__isAvailable = isAvailable
