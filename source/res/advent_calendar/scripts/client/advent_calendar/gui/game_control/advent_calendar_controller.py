# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/game_control/advent_calendar_controller.py
import logging
import re
import Event
from BWUtil import AsyncReturn
from adisp import adisp_process
from advent_calendar.gui.feature.constants import ADVENT_CALENDAR_QUEST_POSTFIX, ADVENT_CALENDAR_TOKEN, ADVENT_CALENDAR_QUEST_PREFIX, ADVENT_CALENDAR_PROGRESSION_QUEST_PREFIX, ADVENT_CALENDAR_QUEST_RE_PATTERN
from advent_calendar.gui.impl.lobby.feature.advent_helper import getQuestNeededTokensCount, getProgressionRewardType
from advent_calendar.gui.impl.lobby.feature.bonus_grouper import QuestRewardsGroups, AdventCalendarQuestsBonusGrouper
from advent_calendar.helpers.server_settings import AdventCalendarConfig
from advent_calendar.skeletons.game_controller import IAdventCalendarController
from advent_calendar_common.advent_calendar_constants import GAME_PARAMS_KEY
from constants import SECONDS_IN_DAY
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.bonuses import LootBoxTokensBonus
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils
from shared_utils import nextTick, first
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from wg_async import wg_async, TimeoutError, BrokenPromiseError, await_callback
_logger = logging.getLogger(__name__)
_TRACKING_CONFIGS = (GAME_PARAMS_KEY, 'isLootBoxesEnabled')
OPEN_DOOR_COMPLETED_TIMEOUT = 5

class AdventCalendarController(IAdventCalendarController):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(AdventCalendarController, self).__init__()
        self.__em = Event.EventManager()
        self.onConfigChanged = Event.Event(self.__em)
        self.onNewDayStarted = Event.Event(self.__em)
        self.onDoorOpened = Event.Event(self.__em)
        self.onLootBoxInfoUpdated = Event.Event(self.__em)
        self.__dayChangeNotifier = SimpleNotifier(self.__getTimeToNextDay, self.__onNotifyDayChange)
        self.__phaseChangedNotifier = SimpleNotifier(self.__getTimeTillPhaseChange, self.onConfigChanged)
        self.__awaitedQuestId = ''
        self.__completedAwardsQuests = None
        self.__progressionRewardsQuestsOrdered = []
        self.__lootBoxInfo = None
        self.__isEnabledPrev = None
        return

    def onLobbyInited(self, event):
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChanged
        self.__hangarSpace.onSpaceCreate += self.__update
        self.__updateLootBoxInfo()
        self.__progressionRewardsQuestsOrdered = self.__getProgressionRewardQuestsOrdered()
        self.__startNotifiers()
        self.__eventsCache.onSyncCompleted += self.__onEventsCacheSynced
        super(AdventCalendarController, self).onLobbyInited(event)

    def onDisconnected(self):
        self.__completedAwardsQuests = None
        self.__progressionRewardsQuestsOrdered = []
        self.__lootBoxInfo = None
        self.__awaitedQuestId = ''
        self.__isEnabledPrev = None
        self.__phaseChangedNotifier.stopNotification()
        self.__dayChangeNotifier.stopNotification()
        super(AdventCalendarController, self).onDisconnected()
        return

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self, True)
        self.__eventsCache.onSyncCompleted -= self.__onEventsCacheSynced
        self.__hangarSpace.onSpaceCreate -= self.__update
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChanged
        self.__phaseChangedNotifier.clear()
        self.__phaseChangedNotifier = None
        self.__dayChangeNotifier.clear()
        self.__dayChangeNotifier = None
        self.__em.clear()
        super(AdventCalendarController, self).fini()
        return

    def isInActivePhase(self):
        return self.postEventStartDate > self.getCurrentTime > self.startDate

    def isAvailableAndActivePhase(self):
        return self.isActive and self.isInActivePhase()

    def isAvailableAndPostActivePhase(self):
        return self.isActive and self.isInPostActivePhase()

    def isAvailable(self):
        return self.isActive and (self.isInActivePhase() or self.isInPostActivePhase())

    def isInPostActivePhase(self):
        return self.postEventEndDate > self.getCurrentTime > self.postEventStartDate

    @property
    def isActive(self):
        return self.isEnabled

    @property
    def isEnabled(self):
        return self.config.isEnabled

    def getCurrentDayNumber(self):
        return int((time_utils.getServerUTCTime() - self.startDate) // SECONDS_IN_DAY + 1)

    def getDoorOpenTimeUI(self, doorId):
        return self.startDate + time_utils.ONE_DAY * (doorId - 1)

    @property
    def startDate(self):
        return self.config.startDate

    @property
    def postEventStartDate(self):
        return self.config.postEventStartDate

    @property
    def postEventEndDate(self):
        return self.config.postEventEndDate

    def getDoorOpenTokenName(self, day=1):
        return self.config.doorOpenTokenMask.format(dayID=day)

    def getDoorOpenQuestName(self, day=1):
        return self.config.doorOpenTokenMask.format(dayID=day)

    @property
    def getCurrentTime(self):
        return time_utils.getServerUTCTime()

    def progressionQuestMayBeCompleted(self, openedDoorsAmount=None):
        if self.isInActivePhase():
            if openedDoorsAmount is None:
                openedDoorsAmount = len(self.completedAwardsQuests)
            for quest in self.progressionRewardQuestsOrdered:
                if getQuestNeededTokensCount(quest) == openedDoorsAmount:
                    return quest

        return

    @wg_async
    def awaitDoorOpenQuestCompletion(self, dayID):
        self.__awaitedQuestId = self.getDoorOpenQuestName(dayID)
        processorResult = None
        try:
            try:
                processorResult = yield await_callback(self.__openAdventCalendarDoor, timeout=OPEN_DOOR_COMPLETED_TIMEOUT)(dayID)
            except TimeoutError:
                _logger.error('Received Timeout error waiting for %s quest completion', self.__awaitedQuestId)
            except BrokenPromiseError:
                _logger.error('%s has been destroyed before %s completed', self, self.__awaitedQuestId)

        finally:
            result = processorResult is not None and processorResult.success

        _logger.info('Door is finally opened.')
        raise AsyncReturn(result)
        return

    def isDoorOpened(self, dayID):
        return self.getDoorOpenTokenName(dayID) in self.completedAwardsQuests

    @property
    def completedAwardsQuests(self):
        if self.__completedAwardsQuests is None:

            def __questCompletedFilterFunc(q):
                return self.__filterFunc(q) and q.isCompleted()

            self.__completedAwardsQuests = self.__eventsCache.getHiddenQuests(__questCompletedFilterFunc)
        return self.__completedAwardsQuests

    def getLootBoxInfo(self):
        if not self.__lootBoxInfo:
            self.__updateLootBoxInfo()
        return self.__lootBoxInfo

    @property
    def progressionRewardQuestsOrdered(self):
        if not self.__progressionRewardsQuestsOrdered:
            self.__progressionRewardsQuestsOrdered = self.__getProgressionRewardQuestsOrdered()
        return self.__progressionRewardsQuestsOrdered

    def getQuestByDayId(self, dayId):
        questID = ADVENT_CALENDAR_QUEST_PREFIX + str(dayId) + ADVENT_CALENDAR_QUEST_POSTFIX
        quest = self.__eventsCache.getHiddenQuests(self.__filterFunc).get(questID)
        if quest is None:
            _logger.error('Quest is not found %s', ADVENT_CALENDAR_QUEST_PREFIX + str(dayId) + ADVENT_CALENDAR_QUEST_POSTFIX)
        return quest

    def getAdventCalendarGroupedQuestsRewards(self):
        questRewards = {QuestRewardsGroups.PROGRESSION_REWARDS: {getProgressionRewardType(first(quest.getBonuses())).value for quest in self.progressionRewardQuestsOrdered}}
        adventCalendarQuests = self.__eventsCache.getHiddenQuests(self.__filterFunc)
        questRewards.update(AdventCalendarQuestsBonusGrouper().group(adventCalendarQuests.values()))
        return questRewards

    @property
    def config(self):
        if self.__lobbyContext:
            rawSettings = self.__lobbyContext.getServerSettings().getSettings().get(GAME_PARAMS_KEY, {})
            return AdventCalendarConfig(**rawSettings)
        return AdventCalendarConfig()

    def __onSettingsChanged(self, diff):
        if any((key in diff for key in _TRACKING_CONFIGS)):
            self.__update()
        if 'lootBoxes_config' in diff:
            self.__updateLootBoxInfo()
        if 'quests' in diff:
            self.__progressionRewardsQuestsOrdered = self.__getProgressionRewardQuestsOrdered()

    def __isEnableChanged(self):
        if self.config.doorsCount == 0:
            self.__isEnabledPrev = None
            return
        elif not self.startDate < self.getCurrentTime < self.postEventEndDate:
            self.__isEnabledPrev = None
            return
        elif self.__isEnabledPrev is None:
            self.__isEnabledPrev = self.config.isEnabled
            return
        else:
            if self.__isEnabledPrev is not self.config.isEnabled:
                self.__isEnabledPrev = self.config.isEnabled
                if self.config.isEnabled:
                    message = R.strings.advent_calendar.notification.event.resumed()
                else:
                    message = R.strings.advent_calendar.notification.event.paused()
                SystemMessages.pushI18nMessage(backport.text(message), type=SM_TYPE.Warning, priority=NotificationPriorityLevel.HIGH)
            return

    def __update(self):
        self.__startNotifiers()
        self.__isEnableChanged()
        self.onConfigChanged()

    def __getTimeToNextDay(self):
        return self.__getDeltaToNextOpenDay() if self.isInActivePhase() else 0

    @staticmethod
    def __getDeltaToNextOpenDay():
        return time_utils.getDayTimeLeft() + 1

    def __onNotifyDayChange(self):
        self.onNewDayStarted()

    @staticmethod
    def __filterFunc(quest):
        qId = quest.getID()
        return bool(re.match(ADVENT_CALENDAR_QUEST_RE_PATTERN, qId))

    def __onDoorSuccessfulOpened(self):
        self.__awaitedQuestId = ''
        self.onDoorOpened()

    def __onTokensUpdate(self, diff):
        if self.isInPostActivePhase():
            return
        for key in diff.keys():
            if key == ADVENT_CALENDAR_TOKEN:
                if self.__awaitedQuestId:
                    return
                return self.onDoorOpened()

    def __getProgressionRewardQuestsOrdered(self):

        def __progressionQuestsFilterFunc(quest):
            return quest.getID().startswith(ADVENT_CALENDAR_PROGRESSION_QUEST_PREFIX.format(id=''))

        quests = self.__eventsCache.getHiddenQuests(__progressionQuestsFilterFunc)
        return sorted(quests.values(), key=getQuestNeededTokensCount)

    def __getRewardsLootBox(self):
        box = None
        for bonus in (q.getBonuses()[0] for q in self.progressionRewardQuestsOrdered):
            if isinstance(bonus, LootBoxTokensBonus):
                for token in bonus.getTokens():
                    box = self.__itemsCache.items.tokens.getLootBoxByTokenID(token)
                    break

        return box

    def __updateLootBoxInfo(self):
        pass

    def __startNotifiers(self):
        if self.isActive:
            self.__phaseChangedNotifier.startNotification()
        if self.isAvailable():
            self.__dayChangeNotifier.startNotification()

    def __getTimeTillPhaseChange(self):
        if self.isActive:
            if self.isInActivePhase():
                return self.postEventStartDate - self.getCurrentTime
            if self.isInPostActivePhase():
                return self.postEventEndDate - self.getCurrentTime
            return max(self.startDate - self.getCurrentTime, 0)

    @nextTick
    def __onEventsCacheSynced(self, *args, **kwargs):
        self.__completedAwardsQuests = None
        self.__progressionRewardsQuestsOrdered = None
        if self.__awaitedQuestId and self.__awaitedQuestId in self.completedAwardsQuests.keys():
            self.__onDoorSuccessfulOpened()
        return

    @adisp_process
    def __openAdventCalendarDoor(self, dayID, callback=None):
        _logger.info('Sending request to open door=%d', dayID)
        from advent_calendar.gui.feature.processor import AdventCalendarDoorsProcessor
        result = yield AdventCalendarDoorsProcessor(int(dayID)).request()
        _logger.info('Result of door open request=%s', result)
        if callback:
            callback(result)
