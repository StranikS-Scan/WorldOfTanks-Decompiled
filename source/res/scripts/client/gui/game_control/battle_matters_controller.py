# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/battle_matters_controller.py
import itertools
import typing
from enum import Enum
import BigWorld
from collections import OrderedDict
from Event import Event, EventManager
from account_helpers import AccountSettings
from account_helpers.AccountSettings import BattleMatters
from constants import Configs, ARENA_BONUS_TYPE
from gui.impl.lobby.battle_matters.battle_matters_constants import SequenceNumber
from PlayerEvents import g_playerEvents
from gui.selectable_reward.constants import SELECTABLE_BONUS_NAME
from gui.selectable_reward.common import BattleMattersSelectableRewardManager
from gui.server_events.bonuses import VehiclesBonus
from gui.server_events.events_constants import BATTLE_MATTERS_QUEST_ID, BATTLE_MATTERS_INTERMEDIATE_QUEST_ID, BATTLE_MATTERS_COMPENSATION_QUEST_ID
from gui.server_events.events_helpers import isAllQuestsCompleted, getIdxFromQuest
from gui.shared.event_dispatcher import showBattleMattersReward
from gui.impl.lobby.battle_matters.battle_matters_hints import BattleMattersHintsHelper
from helpers import dependency, server_settings
from shared_utils import first
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SelectableBonus
_BATTLE_MATTERS_UNLOCK_TOKEN = 'battle_matters_unlock'
_CLIENT_REWARD_IDX = -1

class _FinishState(Enum):
    NOT_INITED = 0
    IS_NOT_FINISHED = 1
    IS_FINISHED = 2


class BattleMattersController(IBattleMattersController):
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __connMgr = dependency.descriptor(IConnectionManager)
    __battleMattersSelectableRewardMgr = BattleMattersSelectableRewardManager
    __bootcampController = dependency.descriptor(IBootcampController)
    __slots__ = ('_em', 'onStateChanged', 'onFinish', '_isEnabled', '_prevFinishStateFlag', '_isPaused', '_isAvailable', '__delayedRewardOfferCurrencyToken', '__delayedRewardOfferVisibilityToken', '__isWaitingToken', '__savedRewards', '__hasDelayedRewards', '__finishState', '__hintHelper', '__progressWatcher')

    def __init__(self):
        super(BattleMattersController, self).__init__()
        self._em = EventManager()
        self.onStateChanged = Event(self._em)
        self.onFinish = Event(self._em)
        self._isEnabled = False
        self._isPaused = False
        self._prevFinishStateFlag = False
        self._isAvailable = False
        self.__delayedRewardOfferCurrencyToken = ''
        self.__delayedRewardOfferVisibilityToken = ''
        self.__savedRewards = {}
        self.__hasDelayedRewards = False
        self.__finishState = _FinishState.NOT_INITED
        self.__hintHelper = None
        self.__isWaitingToken = False
        self.__progressWatcher = None
        return

    @staticmethod
    def isBattleMattersQuest(quest):
        return BattleMattersController.isRegularBattleMattersQuest(quest) or BattleMattersController.isIntermediateBattleMattersQuest(quest) or BattleMattersController.isCompensationBattleMattersQuest(quest)

    @staticmethod
    def isBattleMattersQuestID(questID):
        return BattleMattersController.isRegularBattleMattersQuestID(questID) or BattleMattersController.isIntermediateBattleMattersQuestID(questID) or BattleMattersController.isCompensationBattleMattersQuestID(questID)

    @staticmethod
    def isRegularBattleMattersQuestID(questID):
        return questID.startswith(BATTLE_MATTERS_QUEST_ID)

    @classmethod
    def isRegularBattleMattersQuest(cls, quest):
        return cls.isRegularBattleMattersQuestID(quest.getID())

    @staticmethod
    def isCompensationBattleMattersQuestID(questID):
        return questID.startswith(BATTLE_MATTERS_COMPENSATION_QUEST_ID)

    @classmethod
    def isCompensationBattleMattersQuest(cls, quest):
        return cls.isCompensationBattleMattersQuestID(quest.getID())

    @classmethod
    def isIntermediateBattleMattersQuest(cls, quest):
        return cls.isIntermediateBattleMattersQuestID(quest.getID())

    @staticmethod
    def isIntermediateBattleMattersQuestID(questID):
        return questID.startswith(BATTLE_MATTERS_INTERMEDIATE_QUEST_ID)

    def init(self):
        self.__connMgr.onConnected += self.__onConnected
        if self.__hintHelper is None:
            self.__hintHelper = BattleMattersHintsHelper(self)
        self.__progressWatcher = _BattleMattersProgressWatcher()
        return

    def fini(self):
        self.__connMgr.onConnected -= self.__onConnected
        self._em.clear()
        self._isEnabled = False
        self._isPaused = False
        self.__delayedRewardOfferCurrencyToken = None
        self.__delayedRewardOfferVisibilityToken = None
        self.__savedRewards = None
        if self.__hintHelper:
            self.__hintHelper.fini()
            self.__hintHelper = None
        self.__progressWatcher.fini()
        self.__progressWatcher = None
        return

    def __subscribe(self):
        self.__lobbyContext.onServerSettingsChanged += self._onLobbyServerSettingChanged
        self.__eventsCache.onSyncCompleted += self._onSyncCompleted
        self.__itemsCache.onSyncCompleted += self._onItemsCacheSync
        self.__connMgr.onDisconnected += self.__onDisconnected

    def __unsubscribe(self):
        self.__lobbyContext.onServerSettingsChanged -= self._onLobbyServerSettingChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        self.__eventsCache.onSyncCompleted -= self._onSyncCompleted
        self.__itemsCache.onSyncCompleted -= self._onItemsCacheSync
        self.__connMgr.onDisconnected -= self.__onDisconnected
        self.__progressWatcher.updateState(False)

    def isEnabled(self):
        return self._isEnabled

    def isPaused(self):
        return self._isPaused

    def isFinished(self):
        return isAllQuestsCompleted(self.getRegularBattleMattersQuests())

    def isActive(self):
        return self.isEnabled() and not self.isPaused() and not self.isFinished()

    @property
    def progressWatcher(self):
        return self.__progressWatcher

    def hasDelayedRewards(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.__delayedRewardOfferCurrencyToken) > 0

    def hasDelayedRewardsInQuest(self, quest):
        for bonus in quest.getBonuses():
            if bonus.getName() == SELECTABLE_BONUS_NAME and self.__delayedRewardOfferVisibilityToken in bonus.getValue():
                return True

        return False

    def isFinalQuest(self, quest):
        return quest.getID() == self.getFinalQuest().getID()

    def getFinalQuest(self):
        quests = self.getIntermediateQuests()
        return quests[-1] if quests else None

    def getQuestByIdx(self, questIdx):
        quests = self.getRegularBattleMattersQuests()
        return quests[questIdx] if quests and len(quests) - 1 >= questIdx else None

    def getCompletedBattleMattersQuests(self):
        currentQuest = self.getCurrentQuest()
        currentQuestId = currentQuest.getOrder() if currentQuest else None
        compensationQuests = {q.getOrder():q.isCompleted() for q in self.getCompensationBattleMattersQuests()}

        def userFilterFunc(q):
            return (q.isCompleted() or compensationQuests.get(q.getOrder(), False)) and (currentQuestId is None or q.getOrder() < currentQuestId)

        return self.getRegularBattleMattersQuests(userFilterFunc)

    def getCompletedBattleMattersQuestsCount(self):
        currentQuest = self.getCurrentQuest()
        return currentQuest.getOrder() - 1 if currentQuest else len(self.getCompletedBattleMattersQuests())

    def getNotCompletedBattleMattersQuests(self):
        compensationQuests = {q.getOrder():q.isCompleted() for q in self.getCompensationBattleMattersQuests()}

        def userFilterFunc(q):
            return not (q.isCompleted() or compensationQuests.get(q.getOrder(), False))

        return self.getRegularBattleMattersQuests(userFilterFunc)

    def getQuestsWithDelayedReward(self):

        def filterFunc(quest):
            return any((self.__delayedRewardOfferVisibilityToken in bonus.getTokens() for bonus in quest.getBonuses('tokens')))

        return self.getBattleMattersQuests(filterFunc)

    def getBattleMattersQuests(self, filterFunc=None):
        quests = self.__eventsCache.getHiddenQuests(BattleMattersController.isBattleMattersQuest).values()
        quests = sorted(quests, key=lambda q: q.getOrder())
        if filterFunc:
            return [ quest for quest in quests if filterFunc(quest) ]
        return quests

    def getRegularBattleMattersQuests(self, filterFunc=None):

        def findQuest(quest):
            result = BattleMattersController.isRegularBattleMattersQuest(quest)
            return result if filterFunc is None else result and filterFunc(quest)

        return self.getBattleMattersQuests(findQuest)

    def getCompensationBattleMattersQuests(self, filterFunc=None):

        def findQuest(quest):
            result = BattleMattersController.isCompensationBattleMattersQuest(quest)
            return result if filterFunc is None else result and filterFunc(quest)

        return self.getBattleMattersQuests(findQuest)

    def getIntermediateQuests(self):
        return self.getBattleMattersQuests(BattleMattersController.isIntermediateBattleMattersQuest)

    def getCountBattleMattersQuests(self):
        return len(self.getRegularBattleMattersQuests())

    def getDelayedRewardToken(self):
        return self.__delayedRewardOfferVisibilityToken

    def getDelayedRewardCurrencyToken(self):
        return self.__delayedRewardOfferCurrencyToken

    def hasLinkedIntermediateQuest(self, quest):
        questIdx = getIdxFromQuest(quest)
        intermediateQuests = self.getIntermediateQuests()
        for curQuest in intermediateQuests:
            if questIdx == getIdxFromQuest(curQuest):
                return True

        return False

    def showAwardView(self, questsData, clientCtx=None):
        self.__saveRewards(questsData, clientCtx)
        rewardsOrder = sorted(self.__savedRewards.keys())
        for idx in rewardsOrder:
            isInPair = self.__savedRewards[idx].get('isInPair', False)
            if not isInPair or isInPair and len(self.__savedRewards[idx]['quests']) == 2:
                self._showAward({idx: self.__savedRewards[idx]})
                self.__savedRewards.pop(idx)
            break

    def getCurrentQuest(self):
        quests = self.getNotCompletedBattleMattersQuests()
        return quests[0] if quests else None

    def getQuestProgress(self, quest):
        compensationQuestStatus = {q.getOrder():q.isCompleted() for q in self.getCompensationBattleMattersQuests()}
        currentProgress = 0
        maxProgress = 0
        if quest:
            items = quest.bonusCond.getConditions().items
            item = first(items)
            if item:
                maxProgress = item.getTotalValue()
                if quest.isCompleted() or compensationQuestStatus.get(quest.getOrder(), False):
                    currentProgress = maxProgress
                else:
                    progressID = item.getKey()
                    progressData = quest.getProgressData()
                    progressItems = first(progressData.values(), {})
                    currentProgress = progressItems.get(progressID, 0) if progressID and progressData else currentProgress
        return (currentProgress, maxProgress)

    def getSelectedVehicle(self):
        vehicle = None
        bonus = self.__getVehicleSelectableBonus()
        if bonus:
            options = self.__battleMattersSelectableRewardMgr.getBonusReceivedOptions(bonus)
            for bonus, _ in options:
                if bonus.getName() == VehiclesBonus.VEHICLES_BONUS:
                    vehicle, _ = first(bonus.getVehicles())

        return vehicle

    def hasAccessToken(self):
        return self.__itemsCache.items.tokens.getToken(_BATTLE_MATTERS_UNLOCK_TOKEN) is not None

    def _getIsEnabled(self):
        isEnabled = self.__getConfig().isEnabled and not self.__bootcampController.isInBootcamp()
        return isEnabled and (self._isAvailable or self.__eventsCache.waitForSync or not self.__itemsCache.isSynced())

    def _onSyncCompleted(self):
        self.__update()
        currentQuest = self.getCurrentQuest()
        if currentQuest:
            currentProgress, _ = self.getQuestProgress(currentQuest)
            self.__progressWatcher.onEventsCacheSyncCompleted(currentQuest, currentProgress)
        isFinished = self.isFinished()
        if self._prevFinishStateFlag != isFinished:
            self._prevFinishStateFlag = isFinished
            self.__progressWatcher.updateState(self.isActive())

    def _onItemsCacheSync(self, *_):
        previousIsAvailable = self._isAvailable
        self._isAvailable = self.hasAccessToken()
        if previousIsAvailable != self._isAvailable or self.__hasDelayedRewards or self.hasDelayedRewards():
            if self._isAvailable and self.__isWaitingToken:
                self.__isWaitingToken = False
                self.__eventsCache.onSyncCompleted += self._onSyncCompleted
                self.__lobbyContext.onServerSettingsChanged += self._onLobbyServerSettingChanged
                self.__lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
            self.__update()

    def _onLobbyServerSettingChanged(self, newServerSettings):
        newServerSettings.onServerSettingsChange += self._onServerSettingsChange
        self.__update()

    @server_settings.serverSettingsChangeListener(Configs.BATTLE_MATTERS_CONFIG.value)
    def _onServerSettingsChange(self, _):
        self.__update()

    def _checkIsBattleMattersStateChanged(self):
        config = self.__getConfig()
        isEnabled = self._getIsEnabled()
        isPausedFromConfig = config.isPaused
        delayedRewardOfferCurrencyToken = config.delayedRewardOfferCurrencyToken
        delayedRewardOfferVisibilityToken = config.delayedRewardOfferVisibilityToken
        isChanged = isEnabled != self._isEnabled or self._isPaused != isPausedFromConfig or self.__delayedRewardOfferCurrencyToken != delayedRewardOfferCurrencyToken or self.__delayedRewardOfferVisibilityToken != delayedRewardOfferVisibilityToken
        if isChanged:
            self._isEnabled = isEnabled
            self._isPaused = isPausedFromConfig
            self.__delayedRewardOfferCurrencyToken = delayedRewardOfferCurrencyToken
            self.__delayedRewardOfferVisibilityToken = delayedRewardOfferVisibilityToken
            self.onStateChanged()
            self.__progressWatcher.updateState(self.isActive())
        return isChanged

    @staticmethod
    def _showAward(rewardsDict):
        showBattleMattersReward(rewardsDict)

    def __update(self):
        if self.__cachesAreReady():
            eventSent = self._checkIsBattleMattersStateChanged()
            self.__checkDelayedReward(not eventSent)
            self.__updateFinishState()
            if not self._isAvailable:
                self.__isWaitingToken = True
                self.__eventsCache.onSyncCompleted -= self._onSyncCompleted
                self.__lobbyContext.onServerSettingsChanged -= self._onLobbyServerSettingChanged
                self.__lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange

    def __cachesAreReady(self):
        return not self.__eventsCache.waitForSync and self.__itemsCache.isSynced()

    def __checkDelayedReward(self, eventIsNeeded):
        hasDelayedRewards = self.hasDelayedRewards()
        if hasDelayedRewards != self.__hasDelayedRewards:
            self.__hasDelayedRewards = hasDelayedRewards
            if eventIsNeeded:
                self.onStateChanged()

    def __updateFinishState(self):
        newFinishState = _FinishState.IS_FINISHED if self.isFinished() else _FinishState.IS_NOT_FINISHED
        if newFinishState != self.__finishState:
            self.__finishState = newFinishState
            if self.__finishState != _FinishState.IS_NOT_FINISHED:
                self.onFinish()

    def __onConnected(self):
        self._isAvailable = False
        self.__savedRewards = OrderedDict()
        self.__hasDelayedRewards = False
        self.__finishState = _FinishState.NOT_INITED
        self.__isWaitingToken = False
        self.__subscribe()
        self.__progressWatcher.onConnected()
        if self.__cachesAreReady():
            self._checkIsBattleMattersStateChanged()

    def __onDisconnected(self):
        self.__unsubscribe()
        self.__progressWatcher.onDisconnected()

    def __getVehicleSelectableBonus(self):
        return first(self.__battleMattersSelectableRewardMgr.getSelectableBonuses())

    @classmethod
    def __getConfig(cls):
        return cls.__lobbyContext.getServerSettings().battleMattersConfig

    def __saveRewards(self, questsData, clientCtx=None):
        questIDs = []
        if questsData is not None:
            questIDs = [ qID for qID in questsData.get('completedQuestIDs', set()) if self.isBattleMattersQuestID(qID) ]
        allIntermediateQuests = self.getIntermediateQuests()
        quests = [ q for q in self.getRegularBattleMattersQuests() + self.getCompensationBattleMattersQuests() if q.getID() in questIDs ] if questIDs else []
        intermediateQuests = [ q for q in allIntermediateQuests if q.getID() in questIDs ] if questIDs else []
        questsWithDelayedReward = self.getQuestsWithDelayedReward()
        for questPosition, q in enumerate(quests):
            sequenceNumber = SequenceNumber.SINGLE if len(quests) == 1 else self.__getRewardSequenceNumber(questPosition, len(quests))
            self.__addRewards(q, questsData, isInPair=self.hasLinkedIntermediateQuest(q), sequenceNumber=sequenceNumber)

        for q in intermediateQuests:
            self.__addRewards(q, questsData, isInPair=True)

        for q in questsWithDelayedReward:
            order = q.getOrder()
            if order in self.__savedRewards:
                self.__savedRewards[order].update({'isWithDelayedBonus': True})

        if clientCtx:
            self.__savedRewards[_CLIENT_REWARD_IDX] = clientCtx
        return

    def __addRewards(self, quest, questsData, isInPair, sequenceNumber=None):
        order = quest.getOrder()
        self.__savedRewards.setdefault(order, {}).setdefault('quests', {}).update({quest.getID(): questsData.get('detailedRewards', {}).get(quest.getID(), {})})
        self.__savedRewards[order].update({'isInPair': isInPair})
        if sequenceNumber:
            self.__savedRewards[order].update({'sequenceNumber': sequenceNumber})

    @staticmethod
    def __getRewardSequenceNumber(rewardPosition, questsCount):
        if rewardPosition < 1:
            return SequenceNumber.FIRST
        return SequenceNumber.LAST if rewardPosition == questsCount - 1 else SequenceNumber.MIDDLE


class _BattleMattersProgressWatcher(object):

    def __init__(self):
        super(_BattleMattersProgressWatcher, self).__init__()
        self.__isActive = False
        self.__isJustBackFromBattle = False
        self.__isFirstBattleWithoutProgressInSession = False
        self._em = EventManager()
        self.onProgressReset = Event(self._em)
        self.onBackFromBattle = Event(self._em)
        self.onStateChanged = Event(self._em)

    def fini(self):
        self._em.clear()
        self._em = None
        self.updateState(False)
        return

    def updateState(self, isActive):
        if self.__isActive == isActive:
            return
        self.__isActive = isActive
        if isActive:
            g_playerEvents.onAvatarBecomePlayer += self.__onEnterInBattle
            g_playerEvents.onAvatarBecomeNonPlayer += self.__onBackFromBattle
        else:
            g_playerEvents.onAvatarBecomePlayer -= self.__onEnterInBattle
            g_playerEvents.onAvatarBecomeNonPlayer -= self.__onBackFromBattle
        self.onStateChanged()

    @staticmethod
    def getBattlesCountWithoutProgress():
        return AccountSettings.getBattleMattersSetting(BattleMatters.BATTLES_COUNT_WITHOUT_PROGRESS)

    def isJustBackFromBattle(self, reset=False):
        isJustBackFromBattleFlag = self.__isJustBackFromBattle
        if reset:
            self.resetJustFromBattleFlag()
        return isJustBackFromBattleFlag

    def resetJustFromBattleFlag(self):
        self.__isJustBackFromBattle = False

    def isFirstBattleWithoutProgressInSession(self, reset=False):
        isFirstBattleWithoutProgressInSessionFlag = self.__isFirstBattleWithoutProgressInSession
        if reset:
            self.resetFirstBattleWithoutProgressInSessionFlag()
        return isFirstBattleWithoutProgressInSessionFlag

    def resetFirstBattleWithoutProgressInSessionFlag(self):
        self.__isFirstBattleWithoutProgressInSession = False

    def onEventsCacheSyncCompleted(self, currentQuest, currentProgress):
        curQuestIdx = currentQuest.getOrder()
        questIdx = AccountSettings.getBattleMattersSetting(BattleMatters.QUEST_IDX_FOR_LAST_UPDATED_PROGRESS)
        if questIdx != curQuestIdx:
            AccountSettings.setBattleMattersSetting(BattleMatters.QUEST_IDX_FOR_LAST_UPDATED_PROGRESS, curQuestIdx)
            needReset = True
        else:
            needReset = currentProgress != AccountSettings.getBattleMattersSetting(BattleMatters.LAST_QUEST_PROGRESS)
        if needReset:
            AccountSettings.setBattleMattersSetting(BattleMatters.LAST_QUEST_PROGRESS, currentProgress)
            AccountSettings.setBattleMattersSetting(BattleMatters.BATTLES_COUNT_WITHOUT_PROGRESS, 0)
            self.__isFirstBattleWithoutProgressInSession = True
            self.onProgressReset()

    def onConnected(self):
        self.__isFirstBattleWithoutProgressInSession = True

    def onDisconnected(self):
        self.__isFirstBattleWithoutProgressInSession = False

    def __onBackFromBattle(self):
        if BigWorld.player().arenaBonusType in ARENA_BONUS_TYPE.RANDOM_RANGE or not self.__isFirstBattleWithoutProgressInSession:
            self.__isJustBackFromBattle = True
            self.onBackFromBattle()

    def __onEnterInBattle(self):
        if BigWorld.player().arenaBonusType in itertools.chain(ARENA_BONUS_TYPE.RANDOM_RANGE, (ARENA_BONUS_TYPE.WINBACK,)):
            AccountSettings.setBattleMattersSetting(BattleMatters.BATTLES_COUNT_WITHOUT_PROGRESS, self.getBattlesCountWithoutProgress() + 1)
