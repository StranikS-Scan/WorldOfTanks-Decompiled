# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/session_progress_rewards_controller.py
import BigWorld
from ab_feature_test_token_based_shared import getGroupByFeature
from constants import Configs
from Event import EventManager, Event
from gui.session_progress_rewards.session_progress_rewards_bonus_sorter import bonusSortKeyFunc
from gui.server_events.bonuses import getNonQuestBonuses, splitBonuses, mergeBonuses
from helpers import dependency, time_utils
from helpers.events_handler import EventsHandler
from helpers.server_settings import serverSettingsChangeListener
from session_progress_rewards_common import AB_TEST_FEATURE_NAME, AB_TEST_DEFAULT_GROUP_NAME
from skeletons.gui.game_control import ISessionProgressRewardsController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class SessionProgressRewardsController(ISessionProgressRewardsController, EventsHandler):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(SessionProgressRewardsController, self).__init__()
        self.__eventsManager = EventManager()
        self.onDataUpdated = Event(self.__eventsManager)
        self.__isEnabled = False
        self.__isCompleted = False
        self.__currentStep = 0
        self.__lastRewardGameDay = 0
        self.__rewardsCalendar = []
        self.__gameDayCallbackID = 0

    def fini(self):
        self._unsubscribe()
        self.__cancelGameDayNotify()
        self.__eventsManager.clear()
        self.__isEnabled = False
        self.__isCompleted = False
        self.__currentStep = 0
        self.__lastRewardGameDay = 0
        self.__rewardsCalendar = []

    def onLobbyInited(self, event):
        self._subscribe()
        self.__updateFromServerSettings(notify=False)
        self.__updateFromItemsCache(notify=False)
        self.__scheduleGameDayNotify()

    def onAccountBecomeNonPlayer(self):
        self._unsubscribe()
        self.__cancelGameDayNotify()

    @property
    def isEnabled(self):
        return self.__isEnabled

    @property
    def isCompleted(self):
        return self.__isCompleted

    @property
    def isAvailable(self):
        return self.__isEnabled and not self.__isCompleted

    @property
    def currentStep(self):
        return self.__currentStep

    @property
    def finalStep(self):
        if self.__rewardsCalendar:
            finalStep, _ = self.__rewardsCalendar[-1]
            return finalStep

    @property
    def isRewardWasReceivedToday(self):
        return self.__lastRewardGameDay == time_utils.getServerGameDayTimeInDays()

    @property
    def rewardsCalendar(self):
        return self.__rewardsCalendar

    def getRewardsByStep(self, step):
        return next((rewards for stepNumber, rewards in self.rewardsCalendar if stepNumber == step), [])

    def isLastReward(self, step):
        if not self.__rewardsCalendar:
            return False
        lastStep, _ = self.__rewardsCalendar[-1]
        return lastStep == step

    def _getEvents(self):
        return ((self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged), (self.__itemsCache.onSyncCompleted, self.__onItemsCacheSyncCompleted))

    def __getABTestGroup(self):
        tokenNames = self.__itemsCache.items.tokens.getTokens().keys()
        group = getGroupByFeature(tokenNames, AB_TEST_FEATURE_NAME)
        return group if group else AB_TEST_DEFAULT_GROUP_NAME

    @serverSettingsChangeListener(Configs.SESSION_PROGRESS_REWARDS_CONFIG.value)
    def __onServerSettingsChanged(self, _):
        self.__updateFromServerSettings()

    def __onItemsCacheSyncCompleted(self, _, __):
        self.__updateFromItemsCache()

    def __updateFromServerSettings(self, notify=True):
        hasChanges = False
        config = self.__lobbyContext.getServerSettings().sessionProgressRewardsConfig
        if self.__isEnabled != config.isEnabled:
            self.__isEnabled = config.isEnabled
            hasChanges = True
        rewardsCalendar = self.__collectRewardsCalendar(config)
        if self.__rewardsCalendar != rewardsCalendar:
            self.__rewardsCalendar = rewardsCalendar
            hasChanges = True
        if hasChanges and notify:
            self.onDataUpdated()

    def __updateFromItemsCache(self, notify=True):
        hasChanges = False
        progressRewards = self.__itemsCache.items.sessionProgressRewards
        isCompleted = progressRewards.isCompleted()
        if self.__isCompleted != isCompleted:
            self.__isCompleted = isCompleted
            hasChanges = True
        currentStep = progressRewards.getCurrentStep()
        if self.__currentStep != currentStep:
            self.__currentStep = currentStep
            hasChanges = True
        lastRewardGameDay = progressRewards.getLastRewardGameDay()
        if self.__lastRewardGameDay != lastRewardGameDay:
            self.__lastRewardGameDay = lastRewardGameDay
            hasChanges = True
        if hasChanges and notify:
            self.onDataUpdated()

    def __scheduleGameDayNotify(self):
        self.__cancelGameDayNotify()
        delay = time_utils.getGameDayTimeLeft()
        if delay <= 0:
            delay = time_utils.ONE_DAY
        self.__gameDayCallbackID = BigWorld.callback(delay, self.__onGameDayChanged)

    def __cancelGameDayNotify(self):
        if self.__gameDayCallbackID:
            BigWorld.cancelCallback(self.__gameDayCallbackID)
            self.__gameDayCallbackID = 0

    def __onGameDayChanged(self):
        self.__gameDayCallbackID = 0
        self.onDataUpdated()
        self.__scheduleGameDayNotify()

    def __collectRewardsCalendar(self, config):
        rewards = []
        abTestGroup = self.__getABTestGroup()
        steps = config.groups.get(abTestGroup, {})
        for step in sorted(steps.iterkeys()):
            stepRewards = []
            for bonusType, bonusValue in steps[step].iteritems():
                stepRewards.extend(getNonQuestBonuses(bonusType, bonusValue))

            stepRewards = splitBonuses(mergeBonuses(stepRewards))
            stepRewards.sort(key=bonusSortKeyFunc)
            rewards.append((step, stepRewards))

        return rewards
