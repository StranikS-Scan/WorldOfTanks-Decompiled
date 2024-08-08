# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_anniversary_controller.py
import logging
import typing
import BigWorld
from Event import EventManager, Event
from account_helpers.settings_core.settings_constants import WotAnniversaryStorageKeys
from constants import EVENT_TYPE
from gui.shared.utils.scheduled_notifications import AcyclicNotifier, Notifiable
from gui.wot_anniversary.utils import isAnniversaryWelcomeShowed, showWotAnniversaryWelcomeWindow, isAnniversaryNotificationShowed
from gui.wot_anniversary.wot_anniversary_constants import WOT_ANNIVERSARY_LOGIN_QUESTS_PREFIX, WOT_ANNIVERSARY_PREFIX, WOT_ANNIVERSARY_DAILY_QUEST_PREFIX, WOT_ANNIVERSARY_ALL_MASCOT_BATTLE_QUESTS_PREFIX, WOT_ANNIVERSARY_ALL_MASCOT_REWARD_QUEST
from helpers import dependency, time_utils
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IHangarLoadingController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.wot_anniversary import IWotAnniversaryController
from wot_anniversary_common import WOT_ANNIVERSARY_CONFIG_NAME
if typing.TYPE_CHECKING:
    from helpers.server_settings import WotAnniversaryConfig
_logger = logging.getLogger(__name__)
TOKEN_EXPIRY_DELTA = 20

class WotAnniversaryController(IWotAnniversaryController, Notifiable):
    __hangarLoadingController = dependency.descriptor(IHangarLoadingController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __DAYS_TO_SHOW = 3

    def __init__(self):
        super(WotAnniversaryController, self).__init__()
        self.__em = EventManager()
        self.onSettingsChanged = Event(self.__em)
        self.onEventActivePhaseEnded = Event(self.__em)
        self.onEventWillEndSoon = Event(self.__em)
        self.addNotificators(AcyclicNotifier(self.__getTimeTillActivePhaseEnd, self.__onActivePhaseEnded), AcyclicNotifier(self.__getTimeTillEventWillEndSoon, self.__onEventWillEndSoon))
        self.__lastShownMascotReminderNotification = ''

    def onConnected(self):
        self.__hangarLoadingController.onHangarLoadedAfterLogin += self.__onHangarLoadedAfterLogin

    def onLobbyInited(self, event):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__updateNotifications()

    def onAccountBecomeNonPlayer(self):
        self.__clear()

    def fini(self):
        self.__clear()
        self.__lastShownMascotReminderNotification = ''
        self.clearNotification()

    def onDisconnected(self):
        self.__clear()
        self.__lastShownMascotReminderNotification = ''

    def isEnabled(self):
        return self.getConfig().isEnabled

    def isAvailable(self):
        return self.isEnabled() and self.getConfig().isActive

    def isAvailableAndActivePhase(self):
        return self.isAvailable() and self.isInActivePhase()

    def isActive(self):
        return self.getConfig().isActive

    def getConfig(self):
        return self.__lobbyContext.getServerSettings().wotAnniversaryConfig

    def getQuests(self):
        return self.__eventsCache.getHiddenQuests(lambda quest: quest.getID().startswith(WOT_ANNIVERSARY_PREFIX))

    def getLoginQuests(self):
        filterFunc = lambda quest: quest.getID().startswith(WOT_ANNIVERSARY_LOGIN_QUESTS_PREFIX)
        return self.__eventsCache.getHiddenQuests(filterFunc)

    def getDailyQuests(self):
        filterFunc = lambda quest: quest.getID().startswith(WOT_ANNIVERSARY_DAILY_QUEST_PREFIX) and quest.isStarted()
        return self.__eventsCache.getHiddenQuests(filterFunc)

    def getRewardVehicle(self):
        filterFunc = lambda quest: quest.getID().startswith(WOT_ANNIVERSARY_LOGIN_QUESTS_PREFIX) and quest.getBonuses('vehicles')
        rewardQuest = first(self.__eventsCache.getHiddenQuests(filterFunc).values())
        if rewardQuest:
            for vehBonus in rewardQuest.getBonuses('vehicles'):
                vehicles = vehBonus.getValue()
                for intCD in vehicles.iterkeys():
                    return self.__itemsCache.items.getItemByCD(intCD)

        return None

    def getMascotBattleQuests(self):
        filterFunc = lambda quest: quest.getType() == EVENT_TYPE.BATTLE_QUEST and quest.getID().startswith(WOT_ANNIVERSARY_ALL_MASCOT_BATTLE_QUESTS_PREFIX) and quest.isStarted()
        return self.__eventsCache.getHiddenQuests(filterFunc)

    def getMascotRewardQuests(self):
        filterFunc = lambda quest: quest.getType() == EVENT_TYPE.TOKEN_QUEST and quest.getID().startswith(WOT_ANNIVERSARY_ALL_MASCOT_REWARD_QUEST)
        return self.__eventsCache.getHiddenQuests(filterFunc)

    def isLastDayNow(self):
        return time_utils.getCurrentLocalServerTimestamp() + time_utils.ONE_DAY >= self.getConfig().activePhaseEndTime

    def getUrl(self, urlName):
        return self.getConfig().anniversaryUrls.get(urlName, '')

    def isInActivePhase(self):
        config = self.getConfig()
        return config.startTime < time_utils.getCurrentLocalServerTimestamp() < config.activePhaseEndTime

    def isInPostActivePhase(self):
        currentTime = time_utils.getCurrentLocalServerTimestamp()
        config = self.getConfig()
        return config.activePhaseEndTime < currentTime < config.eventCategoryEndTime

    def isEventWillEndSoonDaysNow(self):
        days = self.__DAYS_TO_SHOW * time_utils.ONE_DAY
        config = self.getConfig()
        return time_utils.getCurrentLocalServerTimestamp() + days >= config.eventCategoryEndTime

    @property
    def lastShownMascotReminderNotification(self):
        return self.__lastShownMascotReminderNotification

    @lastShownMascotReminderNotification.setter
    def lastShownMascotReminderNotification(self, questID):
        self.__lastShownMascotReminderNotification = questID

    def __onServerSettingsChanged(self, diff):
        if WOT_ANNIVERSARY_CONFIG_NAME in diff:
            self.onSettingsChanged()
            self.__updateNotifications()

    def __clear(self):
        self.stopNotification()
        self.__em.clear()
        self.__hangarLoadingController.onHangarLoadedAfterLogin -= self.__onHangarLoadedAfterLogin
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged

    def __onHangarLoadedAfterLogin(self):
        if BigWorld.checkUnattended():
            return
        if self.isAvailableAndActivePhase() and not isAnniversaryWelcomeShowed():
            showWotAnniversaryWelcomeWindow()

    def __updateNotifications(self):
        if self.isAvailable():
            self.startNotification()
        else:
            self.stopNotification()

    def __onActivePhaseEnded(self):
        if self.isAvailable() and self.isInPostActivePhase():
            self.onEventActivePhaseEnded()

    def __getTimeTillActivePhaseEnd(self):
        return max(self.getConfig().activePhaseEndTime - time_utils.getCurrentLocalServerTimestamp(), 0)

    def __onEventWillEndSoon(self):
        if self.isAvailable() and self.isInPostActivePhase() and self.isEventWillEndSoonDaysNow() and not isAnniversaryNotificationShowed(WotAnniversaryStorageKeys.WOT_ANNIVERSARY_EVENT_WILL_END_SOON_NOTIFICATION_SHOWED):
            self.onEventWillEndSoon()

    def __getTimeTillEventWillEndSoon(self):
        days = self.__DAYS_TO_SHOW * time_utils.ONE_DAY
        config = self.getConfig()
        return max(config.eventCategoryEndTime - days - time_utils.getCurrentLocalServerTimestamp(), 0)
