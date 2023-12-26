# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/advent_calendar_v2_controller.py
import logging
import re
import Event
from adisp import adisp_process
from constants import SECONDS_IN_DAY
from shared_utils import nextTick
from BWUtil import AsyncReturn
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen.view_models.views.lobby.advent_calendar.advent_calendar_door_view_model import DoorState
from gui.impl.lobby.advent_calendar_v2.advent_calendar_v2_bonus_groupper import AdventCalendarV2QuestsBonusGrouper, QuestRewardsGroups
from gui.impl.lobby.advent_calendar_v2.advent_calendar_v2_helper import getQuestNeededTokensCount, processProbabilityBonuses, getProgressionRewardType, LootBoxInfo
from gui.shared.advent_calendar_v2_consts import ADVENT_CALENDAR_QUEST_POSTFIX, ADVENT_CALENDAR_TOKEN, ADVENT_CALENDAR_QUEST_PREFIX, ADVENT_CALENDAR_PROGRESSION_QUEST_PREFIX, ADVENT_CALENDAR_QUEST_RE_PATTERN
from gui.impl.lobby.advent_calendar_v2.loot_box_helper import LootBoxHelper
from gui.server_events.bonuses import LootBoxTokensBonus
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils
from helpers.server_settings import _AdventCalendarV2Config, _LootBoxesTooltipConfig
from skeletons.gui.game_control import IAdventCalendarV2Controller, IWalletController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController
from wg_async import AsyncScope, AsyncEvent, wg_await, wg_async, TimeoutError, BrokenPromiseError
_logger = logging.getLogger(__name__)
_TRACKING_CONFIGS = ('advent_calendar_config', 'isLootBoxesEnabled')
QUEST_COMPLETED_TIMEOUT = 20

class AdventCalendarV2Controller(IAdventCalendarV2Controller):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __nyController = dependency.descriptor(INewYearController)
    __wallet = dependency.descriptor(IWalletController)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(AdventCalendarV2Controller, self).__init__()
        self.__em = Event.EventManager()
        self.onConfigChanged = Event.Event(self.__em)
        self.onNewDayStarted = Event.Event(self.__em)
        self.onDoorOpened = Event.Event(self.__em)
        self.onLootBoxInfoUpdated = Event.Event(self.__em)
        self.__dayChangeNotifier = SimpleNotifier(self.__getTimeToNextDay, self.__onNotifyDayChange)
        self.__phaseChangedNotifier = SimpleNotifier(self.__getTimeTillPhaseChange, self.onConfigChanged)
        self.__scope = AsyncScope()
        self.__doorOpenedQuestCompletedEvent = AsyncEvent(scope=self.__scope)
        self.__awaitedQuestId = ''
        self.__adventCalendarCompletedQuests = None
        self.__progressionRewardsQuestsOrdered = []
        self.__lootBoxInfo = None
        self.__firstNotOpen = 0
        self.__doorOpeningFirstStepIsReady = False
        self.__doorOpenResult = False
        return

    def onLobbyInited(self, event):
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChanged
        self.__nyController.onStateChanged += self.__update
        self.__hangarSpace.onSpaceCreate += self.__update
        self.__updateLootBoxInfo()
        self.__progressionRewardsQuestsOrdered = self.__getProgressionRewardQuestsOrdered()
        self.__startNotifiers()
        self.__eventsCache.onSyncCompleted += self.__onEventsCacheSynced
        super(AdventCalendarV2Controller, self).onLobbyInited(event)

    def onDisconnected(self):
        self.__doorOpenResult = False
        self.__adventCalendarCompletedQuests = None
        self.__progressionRewardsQuestsOrdered = []
        self.__lootBoxInfo = None
        self.__firstNotOpen = 0
        self.__doorOpeningFirstStepIsReady = False
        self.__awaitedQuestId = ''
        self.__doorOpenedQuestCompletedEvent.clear()
        self.__phaseChangedNotifier.stopNotification()
        self.__dayChangeNotifier.stopNotification()
        super(AdventCalendarV2Controller, self).onDisconnected()
        return

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self, True)
        self.__eventsCache.onSyncCompleted -= self.__onEventsCacheSynced
        self.__nyController.onStateChanged -= self.__update
        self.__hangarSpace.onSpaceCreate -= self.__update
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChanged
        self.__phaseChangedNotifier.clear()
        self.__phaseChangedNotifier = None
        self.__dayChangeNotifier.clear()
        self.__dayChangeNotifier = None
        self.__scope.destroy()
        super(AdventCalendarV2Controller, self).fini()
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
        lootBox = self.__getRewardsLootBox()
        return self.isEnabled and lootBox is not None and self.__isNewYearSpace() and self.__nyController.isEnabled() and self.__lobbyContext.getServerSettings().isLootBoxesEnabled() and self.__lobbyContext.getServerSettings().isLootBoxEnabled(lootBox.getID())

    @property
    def isEnabled(self):
        return self._config.isEnabled

    @property
    def getOpenedDoorsAmount(self):
        return len(self.completedAdventCalendarAwardsQuests)

    def getCurrentDayNumber(self):
        startDay = self.startDate / SECONDS_IN_DAY
        currentDay = time_utils.getServerGameDay()
        doorDay = currentDay - startDay
        return doorDay + 1

    def getDoorOpenTimeUI(self, doorId):
        return self.startDate + time_utils.ONE_DAY * (doorId - 1)

    @property
    def getMaxDayNumbers(self):
        return len(self.doorsCost)

    @property
    def startDate(self):
        return self._config.startDate

    @property
    def postEventStartDate(self):
        return self._config.postEventStartDate

    @property
    def postEventEndDate(self):
        return self._config.postEventEndDate

    def getDoorOpenTokenName(self, day=1):
        return self._config.doorOpenTokenMask.format(dayID=day)

    def getDoorOpenQuestName(self, day=1):
        return self._config.doorOpenTokenMask.format(dayID=day)

    @property
    def doorsCost(self):
        return self._config.doorsCost

    @property
    def getCurrentTime(self):
        return time_utils.getServerUTCTime()

    def progressionQuestMayBeCompleted(self, openedDoorsAmount=None):
        if self.isInActivePhase():
            openedDoorsAmount = openedDoorsAmount if openedDoorsAmount is not None else self.getOpenedDoorsAmount
            for quest in self.progressionRewardQuestsOrdered:
                if getQuestNeededTokensCount(quest) == openedDoorsAmount:
                    return quest

        return

    @wg_async
    def awaitDoorOpenQuestCompletion(self, dayID, currencyName):
        self.__openAdventCalendarDoor(dayID=dayID, currencyName=currencyName, callback=self.__checkDoorOpenServerResult)
        self.__awaitedQuestId = self.getDoorOpenQuestName(dayID)
        try:
            try:
                yield wg_await(self.__doorOpenedQuestCompletedEvent.wait(), timeout=QUEST_COMPLETED_TIMEOUT)
            except TimeoutError:
                _logger.error('Received Timeout error waiting for %s quest completion', self.__awaitedQuestId)
            except BrokenPromiseError:
                _logger.error('%s has been destroyed before %s completed', self, self.__awaitedQuestId)

        finally:
            result = self.__awaitedQuestId in self.completedAdventCalendarAwardsQuests.keys() and self.__doorOpenResult
            self.__awaitedQuestId = ''
            self.__doorOpenResult = False
            self.__doorOpenedQuestCompletedEvent.clear()

        raise AsyncReturn(result)

    def getDoorState(self, doorId):
        if self.isInPostActivePhase():
            return self.getDoorStateInPostActivePhase(doorId)
        currentDayNumber = self.getCurrentDayNumber()
        if self.isDoorOpen(doorId):
            return DoorState.OPENED
        if (doorId == currentDayNumber or doorId == currentDayNumber - 1) and self.isInActivePhase():
            return DoorState.READY_TO_OPEN
        if doorId > currentDayNumber:
            return DoorState.CLOSED
        if doorId < currentDayNumber:
            return DoorState.EXPIRED
        _logger.warning('Wrong door state for %s', doorId)

    def getDoorStateInPostActivePhase(self, doorId):
        if self.__isFirstNotOpen(doorId):
            if self.__wallet.isAvailable:
                return DoorState.READY_TO_OPEN
            return DoorState.EXPIRED
        elif self.isDoorOpen(doorId):
            return DoorState.OPENED
        else:
            return DoorState.EXPIRED

    def getAvailableDoorsToOpenAmount(self):
        return len([ doorId for doorId in range(0, self.getMaxDayNumbers) if self.getDoorState(doorId + 1) == DoorState.READY_TO_OPEN ])

    def isDoorOpen(self, doorID):
        return self.getDoorOpenTokenName(doorID) in self.completedAdventCalendarAwardsQuests

    @property
    def completedAdventCalendarAwardsQuests(self):
        if self.__adventCalendarCompletedQuests is None:

            def __questCompletedFilterFunc(q):
                return self.__filterFunc(q) and q.isCompleted()

            self.__adventCalendarCompletedQuests = self.__eventsCache.getHiddenQuests(__questCompletedFilterFunc)
        return self.__adventCalendarCompletedQuests

    def getLootBoxInfo(self):
        if not self.__lootBoxInfo:
            self.__updateLootBoxInfo()
        return self.__lootBoxInfo

    @property
    def progressionRewardQuestsOrdered(self):
        if not self.__progressionRewardsQuestsOrdered:
            self.__progressionRewardsQuestsOrdered = self.__getProgressionRewardQuestsOrdered()
        return self.__progressionRewardsQuestsOrdered

    def getRewardsForQuest(self, dayId):
        quest = self.__eventsCache.getQuestByID(ADVENT_CALENDAR_QUEST_PREFIX + str(dayId) + ADVENT_CALENDAR_QUEST_POSTFIX)
        if quest is None:
            _logger.error('Quest is not found %s', ADVENT_CALENDAR_QUEST_PREFIX + str(dayId) + ADVENT_CALENDAR_QUEST_POSTFIX)
            return
        else:
            return quest.getBonuses()

    def getAdventCalendarGroupedQuestsRewards(self):
        questRewards = {QuestRewardsGroups.PROGRESSION_REWARDS: {getProgressionRewardType(quest).value for quest in self.progressionRewardQuestsOrdered}}
        adventCalendarQuests = self.__eventsCache.getHiddenQuests(self.__filterFunc)
        questRewards.update(AdventCalendarV2QuestsBonusGrouper().group(adventCalendarQuests.values()))
        return questRewards

    def _getDeltaToNextOpenDay(self):
        return time_utils.getDayTimeLeft() + 1

    @property
    def _config(self):
        return self.__lobbyContext.getServerSettings().adventCalendarV2 if self.__lobbyContext else _AdventCalendarV2Config()

    @property
    def _lootBoxesTooltipConfig(self):
        return self.__lobbyContext.getServerSettings().lootBoxesTooltipConfig if self.__lobbyContext else _LootBoxesTooltipConfig()

    def __isNewYearSpace(self):
        return 'newyear' in self.__hangarSpace.spacePath

    def __isFirstNotOpen(self, dayId):
        if not self.__firstNotOpen:
            for i in range(1, self.getMaxDayNumbers + 1):
                if not self.isDoorOpen(i):
                    self.__firstNotOpen = i
                    break

        return self.__firstNotOpen == dayId

    def __onSettingsChanged(self, diff):
        if any((key in diff for key in _TRACKING_CONFIGS)):
            self.__update()
        if 'lootBoxes_config' in diff:
            self.__updateLootBoxInfo()
        if 'quests' in diff:
            self.__progressionRewardsQuestsOrdered = self.__getProgressionRewardQuestsOrdered()

    def __update(self):
        self.__startNotifiers()
        self.onConfigChanged()

    def __getTimeToNextDay(self):
        return self._getDeltaToNextOpenDay() if self.isInActivePhase() else 0

    def __onNotifyDayChange(self):
        self.onNewDayStarted()

    @staticmethod
    def __filterFunc(quest):
        qId = quest.getID()
        return bool(re.match(ADVENT_CALENDAR_QUEST_RE_PATTERN, qId))

    def __onDoorSuccesfulyOpened(self):
        self.__doorOpeningFirstStepIsReady = False
        self.__firstNotOpen = 0
        self.__doorOpenedQuestCompletedEvent.set()
        self.onDoorOpened()

    def __onTokensUpdate(self, diff):
        if self.isInPostActivePhase():
            return
        for key in diff.keys():
            if key == ADVENT_CALENDAR_TOKEN:
                if not self.__doorOpeningFirstStepIsReady:
                    self.__doorOpeningFirstStepIsReady = True
                    return
                return self.__onDoorSuccesfulyOpened()

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
        box = self.__getRewardsLootBox()
        if box:
            rawBonuses = self._lootBoxesTooltipConfig.boxes.get(box.getID())
            if rawBonuses is not None:
                bonuses = LootBoxHelper.getLootBoxBonuses(rawBonuses.copy())
                if bonuses:
                    self.__lootBoxInfo = LootBoxInfo(id=box.getID(), name=box.getUserName(), category=box.getCategory(), bonuses=processProbabilityBonuses(bonuses))
                    self.onLootBoxInfoUpdated()
            else:
                _logger.warning('No bonuses for lootbox %d were found', box.getID())
        else:
            _logger.warning('No LootBox bonuses for progression quests')
        return

    def __startNotifiers(self):
        if self.isAvailable():
            self.__dayChangeNotifier.startNotification()
            self.__phaseChangedNotifier.startNotification()

    def __getTimeTillPhaseChange(self):
        if self.isAvailable():
            if self.isInActivePhase():
                return self.postEventStartDate - self.getCurrentTime
            return self.postEventEndDate - self.getCurrentTime

    @nextTick
    def __onEventsCacheSynced(self, *args, **kwargs):
        self.__adventCalendarCompletedQuests = None
        if self.__awaitedQuestId and self.__awaitedQuestId in self.completedAdventCalendarAwardsQuests.keys():
            if self.isInActivePhase():
                if not self.__doorOpeningFirstStepIsReady:
                    self.__doorOpeningFirstStepIsReady = True
                    return
                return self.__onDoorSuccesfulyOpened()
            if self.isInPostActivePhase():
                self.__onDoorSuccesfulyOpened()
        return

    def __checkDoorOpenServerResult(self, processorResult):
        if not processorResult.success:
            self.__doorOpenResult = False
            self.__doorOpeningFirstStepIsReady = False
            self.__firstNotOpen = 0
            return self.__doorOpenedQuestCompletedEvent.set()
        self.__doorOpenResult = True

    @adisp_process
    def __openAdventCalendarDoor(self, dayID, currencyName='', callback=None):
        from gui.shared.gui_items.processors.advent_calendar_v2_processor import AdventCalendarDoorsProcessor
        _logger.debug('Sending request to open door=%d, currency=%s', dayID, currencyName)
        result = yield AdventCalendarDoorsProcessor(int(dayID), currencyName).request()
        _logger.debug('Result of door open request=%s', result)
        if callback:
            callback(processorResult=result)
