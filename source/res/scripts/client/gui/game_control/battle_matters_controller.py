# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/battle_matters_controller.py
import typing
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from Event import Event, EventManager
from constants import Configs, QUEUE_TYPE
from gui.prb_control.entities.listener import IGlobalListener
from gui.selectable_reward.constants import SELECTABLE_BONUS_NAME
from gui.selectable_reward.common import BattleMattersSelectableRewardManager
from gui.server_events.bonuses import VehiclesBonus
from gui.server_events.events_constants import BATTLE_MATTERS_QUEST_ID, BATTLE_MATTERS_INTERMEDIATE_QUEST_ID
from gui.server_events.events_helpers import isAllQuestsCompleted, getIdxFromQuest
from gui.shared.event_dispatcher import showBattleMattersReward
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from helpers import dependency, server_settings
from PlayerEvents import g_playerEvents
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore, ISettingsCache
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
from tutorial.control.context import GLOBAL_FLAG
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SelectableBonus
_SNDID_ACHIEVEMENT = 'result_screen_achievements'
_SNDID_BONUS = 'result_screen_bonus'
_HMTL_STRING_FORMAT_PATH = 'html_templates:lobby/quests/linkedSet'
_HMTL_STRING_FORMAT_DESC_KEY = 'awardWindowDescTemplate'
_HMTL_STRING_FORMAT_HINT_DESC_KEY = 'awardWindowHintDescTemplate'
_BATTLE_MATTERS_UNLOCK_TOKEN = 'battle_matters_unlock'
_CLIENT_REWARD_IDX = -1

class BattleMattersController(IBattleMattersController, IGlobalListener):
    __appLoader = dependency.descriptor(IAppLoader)
    __battleResults = dependency.descriptor(IBattleResultsService)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __settingsCache = dependency.descriptor(ISettingsCache)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __connMgr = dependency.descriptor(IConnectionManager)
    __battleMattersSelectableRewardMgr = BattleMattersSelectableRewardManager

    def __init__(self):
        self.needToShowAward = False
        self._em = EventManager()
        self.onStateChanged = Event(self._em)
        self._isEnabled = False
        self._isPaused = False
        self.__delayedRewardOfferCurrencyToken = ''
        self.__delayedRewardOfferVisibilityToken = ''
        self.__entryPointHintShowed = False
        self.__savedRewards = {}
        self.__hasDelayedRewards = False

    @staticmethod
    def isBattleMattersQuest(quest):
        return BattleMattersController.isRegularBattleMattersQuest(quest) or BattleMattersController.isIntermediateBattleMattersQuest(quest)

    @staticmethod
    def isRegularBattleMattersQuestID(questID):
        return questID.startswith(BATTLE_MATTERS_QUEST_ID)

    @classmethod
    def isRegularBattleMattersQuest(cls, quest):
        return cls.isRegularBattleMattersQuestID(quest.getID())

    @classmethod
    def isIntermediateBattleMattersQuest(cls, quest):
        return cls.isIntermediateBattleMattersQuestID(quest.getID())

    @staticmethod
    def isIntermediateBattleMattersQuestID(questID):
        return questID.startswith(BATTLE_MATTERS_INTERMEDIATE_QUEST_ID)

    def init(self):
        self.__lobbyContext.onServerSettingsChanged += self._onLobbyServerSettingChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        self.__eventsCache.onSyncCompleted += self._onSyncCompleted
        self.__itemsCache.onSyncCompleted += self._onItemsCacheSync
        self.__settingsCache.onSyncCompleted += self.__onSettingsCacheSynced
        self.__connMgr.onConnected += self.__onConnected
        g_playerEvents.onPrbDispatcherCreated += self.__onPrbDispatcherCreated
        g_playerEvents.onDisconnected += self.__onDisconnected
        self._isEnabled = self._getIsEnabled()
        config = self.__getConfig()
        self._isPaused = config.isPaused
        self.__delayedRewardOfferCurrencyToken = config.delayedRewardOfferCurrencyToken
        self.__delayedRewardOfferVisibilityToken = config.delayedRewardOfferVisibilityToken

    def fini(self):
        self._em.clear()
        self.__lobbyContext.onServerSettingsChanged -= self._onLobbyServerSettingChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        self.__eventsCache.onSyncCompleted -= self._onSyncCompleted
        self.__itemsCache.onSyncCompleted -= self._onItemsCacheSync
        self.__connMgr.onConnected -= self.__onConnected
        g_playerEvents.onPrbDispatcherCreated -= self.__onPrbDispatcherCreated
        g_playerEvents.onDisconnected -= self.__onDisconnected
        self.__settingsCache.onSyncCompleted -= self.__onSettingsCacheSynced
        self.stopGlobalListening()
        self._isEnabled = False
        self._isPaused = False
        self.__delayedRewardOfferCurrencyToken = None
        self.__delayedRewardOfferVisibilityToken = None
        self.__savedRewards = None
        return

    def isEnabled(self):
        return self._isEnabled

    def isPaused(self):
        return self._isPaused

    def isFinished(self):
        return isAllQuestsCompleted(self.getRegularBattleMattersQuests())

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

        def userFilterFunc(q):
            return q.isCompleted()

        return self.getRegularBattleMattersQuests(userFilterFunc)

    def getNotCompletedBattleMattersQuests(self):

        def userFilterFunc(q):
            return not q.isCompleted()

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
        items = quest.bonusCond.getConditions().items
        currentProgress = 0
        maxProgress = 0
        item = first(items)
        if item:
            maxProgress = item.getTotalValue()
            if quest.isCompleted():
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

    def onPrbEntitySwitched(self):
        self.__updateFightBtnHint()

    def _getIsEnabled(self):
        isEnabled = self.__getConfig().isEnabled
        isAvailable = self.__itemsCache.items.tokens.getTokens().get(_BATTLE_MATTERS_UNLOCK_TOKEN) is not None
        return isEnabled and (isAvailable or self.__eventsCache.waitForSync or self.__itemsCache.waitForSync)

    def _onSyncCompleted(self):
        self._checkIsBattleMattersStateChanged()
        self.__checkEntryPointTrigger()
        hasDelayedRewards = self.hasDelayedRewards()
        if hasDelayedRewards != self.__hasDelayedRewards:
            self.__hasDelayedRewards = hasDelayedRewards

    def _onItemsCacheSync(self, *_):
        hasDelayedRewards = self.hasDelayedRewards()
        if hasDelayedRewards != self.__hasDelayedRewards:
            self.__hasDelayedRewards = hasDelayedRewards
            self.onStateChanged()

    def _onLobbyServerSettingChanged(self, newServerSettings):
        newServerSettings.onServerSettingsChange += self._onServerSettingsChange
        self._checkIsBattleMattersStateChanged()

    @server_settings.serverSettingsChangeListener(Configs.BATTLE_MATTERS_CONFIG.value)
    def _onServerSettingsChange(self, _):
        self._checkIsBattleMattersStateChanged()

    def _checkIsBattleMattersStateChanged(self):
        config = self.__getConfig()
        isEnabledFromConfig = self._getIsEnabled()
        isPausedFromConfig = config.isPaused
        delayedRewardOfferCurrencyToken = config.delayedRewardOfferCurrencyToken
        delayedRewardOfferVisibilityToken = config.delayedRewardOfferVisibilityToken
        isChanged = isEnabledFromConfig != self._isEnabled or self._isPaused != isPausedFromConfig or self.__delayedRewardOfferCurrencyToken != delayedRewardOfferCurrencyToken or self.__delayedRewardOfferVisibilityToken != delayedRewardOfferVisibilityToken
        if isChanged:
            self._isEnabled = isEnabledFromConfig
            self._isPaused = isPausedFromConfig
            self.__delayedRewardOfferCurrencyToken = delayedRewardOfferCurrencyToken
            self.__delayedRewardOfferVisibilityToken = delayedRewardOfferVisibilityToken
            self.onStateChanged()
        return isChanged

    @staticmethod
    def _showAward(rewardsDict):
        showBattleMattersReward(rewardsDict)

    def __onConnected(self):
        self.__lobbyContext.onServerSettingsChanged += self._onLobbyServerSettingChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        self._checkIsBattleMattersStateChanged()

    def __getVehicleSelectableBonus(self):
        return first(self.__battleMattersSelectableRewardMgr.getSelectableBonuses())

    @classmethod
    def __getConfig(cls):
        return cls.__lobbyContext.getServerSettings().battleMattersConfig

    def __onDisconnected(self):
        tutorialStorage = getTutorialGlobalStorage()
        tutorialStorage.setValue(GLOBAL_FLAG.BATTLE_MATTERS_FIGHT_BTN, False)
        tutorialStorage.setValue(GLOBAL_FLAG.BATTLE_MATTERS_ENTRY_POINT, False)

    def __onPrbDispatcherCreated(self):
        self.__checkFightBtnHint()

    def __onSettingsCacheSynced(self):
        self.__checkEntryPointTrigger()
        self.__settingsCache.onSyncCompleted -= self.__onSettingsCacheSynced

    def __checkFightBtnHint(self):
        if self._isEnabled and not self._isPaused and not self.__isHintShowed(OnceOnlyHints.BATTLE_MATTERS_FIGHT_BUTTON_HINT):
            quests = self.getRegularBattleMattersQuests()
            if quests:
                if not quests[0].isCompleted():
                    self.startGlobalListening()
                    self.__updateFightBtnHint()
                else:
                    self.stopGlobalListening()

    def __updateFightBtnHint(self):
        if self.prbEntity is not None:
            isRandom = self.prbEntity.getQueueType() == QUEUE_TYPE.RANDOMS
            getTutorialGlobalStorage().setValue(GLOBAL_FLAG.BATTLE_MATTERS_FIGHT_BTN, isRandom)
        return

    def __isHintShowed(self, triggerName):
        return bool(self.__settingsCore.serverSettings.getOnceOnlyHintsSetting(triggerName, default=False))

    def __checkEntryPointTrigger(self):
        isSynced = self.__settingsCache.isSynced()
        if isSynced and self._isEnabled and not self._isPaused and not self.__entryPointHintShowed:
            self.__entryPointHintShowed = self.__isHintShowed(OnceOnlyHints.BATTLE_MATTERS_ENTRY_POINT_BUTTON_HINT)
            if not self.__entryPointHintShowed and len(self.getCompletedBattleMattersQuests()) == 1:
                getTutorialGlobalStorage().setValue(GLOBAL_FLAG.BATTLE_MATTERS_ENTRY_POINT, True)

    def __pushStatusNotification(self):
        if self.isPaused() or not self.isEnabled():
            self.__systemMessages.proto.serviceChannel.pushClientMessage({}, SCH_CLIENT_MSG_TYPE.BATTLE_MATTERS_PAUSED)
            return
        self.__systemMessages.proto.serviceChannel.pushClientMessage({}, SCH_CLIENT_MSG_TYPE.BATTLE_MATTERS_STARTED)

    def __saveRewards(self, questsData, clientCtx=None):
        questIDs = []
        if questsData is not None:
            questIDs = [ qID for qID in questsData.get('completedQuestIDs', set()) if self.isRegularBattleMattersQuestID(qID) or self.isIntermediateBattleMattersQuestID(qID) ]
        allIntermediateQuests = self.getIntermediateQuests()
        quests = [ q for q in self.getRegularBattleMattersQuests() if q.getID() in questIDs ] if questIDs else []
        intermediateQuests = [ q for q in allIntermediateQuests if q.getID() in questIDs ] if questIDs else []
        questsWithDelayedReward = self.getQuestsWithDelayedReward()
        for q in quests:
            self.__addRewards(q, questsData, isInPair=self.hasLinkedIntermediateQuest(q))

        for q in intermediateQuests:
            self.__addRewards(q, questsData, isInPair=True)

        for q in questsWithDelayedReward:
            order = q.getOrder()
            if order in self.__savedRewards:
                self.__savedRewards[order].update({'isWithDelayedBonus': True})

        if clientCtx:
            self.__savedRewards[_CLIENT_REWARD_IDX] = clientCtx
        return

    def __addRewards(self, quest, questsData, isInPair):
        order = quest.getOrder()
        self.__savedRewards.setdefault(order, {}).setdefault('quests', {}).update({quest.getID(): questsData.get('detailedRewards', {}).get(quest.getID(), {})})
        self.__savedRewards[order].update({'isInPair': isInPair})
