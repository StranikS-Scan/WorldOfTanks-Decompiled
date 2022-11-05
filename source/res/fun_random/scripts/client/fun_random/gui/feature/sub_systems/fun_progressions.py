# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/sub_systems/fun_progressions.py
import typing
from fun_random.helpers.server_settings import FunMetaProgressionConfig, FunProgressionConfig
from fun_random.gui.feature.fun_constants import PROGRESSION_COUNTER_TEMPLATE, PROGRESSION_TRIGGER_TEMPLATE, PROGRESSION_EXECUTOR_TEMPLATE, FEP_PROGRESSION_EXECUTOR_QUEST_ID, FunTimersShifts
from fun_random.gui.feature.models.progressions import FunProgression
from fun_random.gui.shared.events import FunEventType
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.event_bus import SharedEvent
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier, TimerNotifier
from helpers import dependency, time_utils
from skeletons.gui.game_control import IFunRandomController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
from shared_utils import first
if typing.TYPE_CHECKING:
    from skeletons.gui.shared.utils.requesters import ITokensRequester

class FunProgressions(IFunRandomController.IFunProgressions, Notifiable):
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, subscription):
        super(FunProgressions, self).__init__()
        self.__activeProgression = None
        self.__progressionTimestamp = 0
        self.__settings = None
        self.__subscription = subscription
        self.addNotificator(SimpleNotifier(self.getProgressionTimer, self.__invalidateProgressions))
        self.addNotificator(TimerNotifier(self.getProgressionTimer, self.__onProgressionTick))
        return

    def fini(self):
        self.clearNotification()

    def clear(self):
        self.__activeProgression = None
        self.__progressionTimestamp = 0
        self.__settings = None
        return

    def isProgressionExecutor(self, questID):
        return questID.startswith(FEP_PROGRESSION_EXECUTOR_QUEST_ID)

    def getActiveProgression(self):
        return self.__activeProgression

    def getProgressionTimer(self):
        return time_utils.getTimeDeltaFromNowInLocal(self.__progressionTimestamp)

    def getSettings(self):
        return self.__settings

    def startProgressListening(self):
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)
        self.__eventsCache.onSyncCompleted += self.__onEventsSyncCompleted
        self.startNotification()

    def stopProgressListening(self):
        self.stopNotification()
        self.__eventsCache.onSyncCompleted -= self.__onEventsSyncCompleted
        g_clientUpdateManager.removeObjectCallbacks(self)

    def updateSettings(self, progressionSettings):
        if self.__settings != progressionSettings:
            self.__settings = progressionSettings
            self.__invalidateProgressions()

    def __onEventsSyncCompleted(self, *_):
        self.__invalidateProgressions()

    def __onTokensUpdate(self, diff):
        if self.__activeProgression is None:
            return
        else:
            activeCounterName = self.__activeProgression.condition.counterName
            if activeCounterName not in diff:
                return
            activeCounterAmount = self.__itemsCache.items.tokens.getTokenCount(activeCounterName)
            if activeCounterAmount == self.__activeProgression.condition.counter:
                return
            self.__activeProgression.updateCounter(self.__itemsCache.items.tokens.getTokenCount(activeCounterName))
            self.__onProgressionUpdate()
            return

    def __onProgressionTick(self):
        self.__invokeProgressionEvent(FunEventType.PROGRESSION_TICK)

    def __onProgressionUpdate(self):
        self.__invokeProgressionEvent(FunEventType.PROGRESSION_UPDATE)

    def __invokeProgressionEvent(self, eventType):
        self.__subscription.handleEvent(SharedEvent(eventType))

    def __buildActiveProgression(self, quests):
        tokens, now = self.__itemsCache.items.tokens, time_utils.getCurrentTimestamp()
        quests = {qID:quest for qID, quest in quests.iteritems() if quest.isRawAvailable(now)}
        firstName, lastName = self.__settings.progressions[0].name, self.__settings.progressions[-1].name
        return first((self.__buildProgression(pConfig, pConfig.name == firstName, pConfig.name == lastName, quests, tokens) for pConfig in self.__settings.progressions))

    def __buildProgression(self, pConfig, isFirst, isLast, quests, tokens):
        executors = tuple((quests.get(PROGRESSION_EXECUTOR_TEMPLATE.format(pConfig.name, amount)) for amount in pConfig.executors))
        trigger = quests.get(PROGRESSION_TRIGGER_TEMPLATE.format(pConfig.name))
        if trigger is None or not executors or not all(executors):
            return
        else:
            counter = tokens.getTokenCount(PROGRESSION_COUNTER_TEMPLATE.format(pConfig.name))
            return FunProgression(pConfig, isFirst, isLast, counter, trigger, executors)

    def __invalidateProgressions(self):
        isEnabled = self.__settings.isEnabled and self.__eventsCache.isStarted
        quests = self.__eventsCache.getHiddenQuests() if isEnabled else {}
        self.__activeProgression = newProgression = self.__buildActiveProgression(quests) if isEnabled else None
        self.__progressionTimestamp = self.__recalculateProgressionTimer(quests, newProgression) if isEnabled else 0
        self.__onProgressionUpdate()
        self.startNotification()
        return

    def __recalculateProgressionTimer(self, quests, newProgression):
        now = time_utils.getCurrentTimestamp()
        progressionNames = (pConfig.name for pConfig in self.__settings.progressions)
        progressionReset = newProgression.condition.resetTimestamp if newProgression is not None else 0
        triggers = (quests.get(PROGRESSION_TRIGGER_TEMPLATE.format(name)) for name in progressionNames)
        triggersStarts = tuple((trigger.getStartTimeRaw() for trigger in triggers if trigger is not None))
        allTimers = tuple((timer for timer in triggersStarts + (progressionReset,) if timer > now))
        return min(allTimers) + FunTimersShifts.PROGRESSION if allTimers else 0
