# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/battle_matters_controller.py
import typing
from enum import Enum
import BigWorld
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from Event import Event, EventManager
from constants import Configs, QUEUE_TYPE, ARENA_BONUS_TYPE, IS_DEVELOPMENT
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.selectable_reward.constants import SELECTABLE_BONUS_NAME
from gui.selectable_reward.common import BattleMattersSelectableRewardManager
from gui.server_events.bonuses import VehiclesBonus
from gui.server_events.events_constants import BATTLE_MATTERS_QUEST_ID, BATTLE_MATTERS_INTERMEDIATE_QUEST_ID
from gui.server_events.events_helpers import isAllQuestsCompleted, getIdxFromQuest
from gui.shared.event_dispatcher import showBattleMattersReward
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.TUTORIAL_TRIGGER_TYPES import TUTORIAL_TRIGGER_TYPES
from helpers import dependency, server_settings
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
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
from skeletons.tutorial import ITutorialLoader
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

class _FinishState(Enum):
    NOT_INITED = 0
    IS_NOT_FINISHED = 1
    IS_FINISHED = 2


class BattleMattersController(IBattleMattersController):
    __appLoader = dependency.descriptor(IAppLoader)
    __battleResults = dependency.descriptor(IBattleResultsService)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __connMgr = dependency.descriptor(IConnectionManager)
    __battleMattersSelectableRewardMgr = BattleMattersSelectableRewardManager
    __slots__ = ('needToShowAward', '_em', 'onStateChanged', 'onFinish', '_isEnabled', '_isPaused', '_isAvailable', '__delayedRewardOfferCurrencyToken', '__delayedRewardOfferVisibilityToken', '__isWaitingToken', '__savedRewards', '__hasDelayedRewards', '__finishState', '__hintHelper')

    def __init__(self):
        self.needToShowAward = False
        self._em = EventManager()
        self.onStateChanged = Event(self._em)
        self.onFinish = Event(self._em)
        self._isEnabled = False
        self._isPaused = False
        self._isAvailable = False
        self.__delayedRewardOfferCurrencyToken = ''
        self.__delayedRewardOfferVisibilityToken = ''
        self.__savedRewards = {}
        self.__hasDelayedRewards = False
        self.__finishState = _FinishState.NOT_INITED
        self.__hintHelper = None
        self.__isWaitingToken = False
        return

    @staticmethod
    def isBattleMattersQuest(quest):
        return BattleMattersController.isRegularBattleMattersQuest(quest) or BattleMattersController.isIntermediateBattleMattersQuest(quest)

    @staticmethod
    def isBattleMattersQuestID(questID):
        return BattleMattersController.isRegularBattleMattersQuestID(questID) or BattleMattersController.isIntermediateBattleMattersQuestID(questID)

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
        self.__connMgr.onConnected += self.__onConnected
        if self.__hintHelper is None:
            self.__hintHelper = _BattleMattersHintsHelper(self)
        return

    def fini(self):
        self._em.clear()
        self.__lobbyContext.onServerSettingsChanged -= self._onLobbyServerSettingChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        self.__eventsCache.onSyncCompleted -= self._onSyncCompleted
        self.__itemsCache.onSyncCompleted -= self._onItemsCacheSync
        self.__connMgr.onConnected -= self.__onConnected
        self._isEnabled = False
        self._isPaused = False
        self.__delayedRewardOfferCurrencyToken = None
        self.__delayedRewardOfferVisibilityToken = None
        self.__savedRewards = None
        if self.__hintHelper:
            self.__hintHelper.fini()
            self.__hintHelper = None
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

    def _getIsEnabled(self):
        isEnabled = self.__getConfig().isEnabled
        return isEnabled and (self._isAvailable or self.__eventsCache.waitForSync or not self.__itemsCache.isSynced())

    def _onSyncCompleted(self):
        self.__update()

    def _onItemsCacheSync(self, *_):
        self._isAvailable = self.__isAvailableForPlayer()
        if self._isAvailable:
            if self.__isWaitingToken:
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
        return isChanged

    @staticmethod
    def _showAward(rewardsDict):
        showBattleMattersReward(rewardsDict)

    def __isAvailableForPlayer(self):
        return self.__itemsCache.items.tokens.getToken(_BATTLE_MATTERS_UNLOCK_TOKEN) is not None

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
        self.__savedRewards = {}
        self.__hasDelayedRewards = False
        self.__finishState = _FinishState.NOT_INITED
        self.__isWaitingToken = False
        self.__lobbyContext.onServerSettingsChanged += self._onLobbyServerSettingChanged
        self.__eventsCache.onSyncCompleted += self._onSyncCompleted
        self.__itemsCache.onSyncCompleted += self._onItemsCacheSync
        if self.__cachesAreReady():
            self._checkIsBattleMattersStateChanged()

    def __getVehicleSelectableBonus(self):
        return first(self.__battleMattersSelectableRewardMgr.getSelectableBonuses())

    @classmethod
    def __getConfig(cls):
        return cls.__lobbyContext.getServerSettings().battleMattersConfig

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


class _BattleMattersHintsHelper(object):
    __eventsCache = dependency.descriptor(IEventsCache)
    __settingsCache = dependency.descriptor(ISettingsCache)
    __slots__ = ('__hints', '__isSynced', '__hasHintListeners', '__battleMattersController')

    def __init__(self, controller):
        super(_BattleMattersHintsHelper, self).__init__()
        self.__isSynced = False
        self.__hasHintListeners = False
        self.__battleMattersController = controller
        self.__hints = self.__getDefaultHints(controller)
        self.__addHintsListeners()
        g_playerEvents.onDisconnected += self.__onDisconnected

    def fini(self):
        self.__isSynced = False
        self.__removeHintsListeners()
        g_playerEvents.onDisconnected -= self.__onDisconnected
        self.__battleMattersController = None
        self.__stopHints()
        return

    @staticmethod
    def __getDefaultHints(controller):
        return (_EntryPointHint(controller), _FightBtnMultiShowHint(controller))

    def __addHintsListeners(self):
        self.__hasHintListeners = True
        self.__eventsCache.onSyncCompleted += self.__onSyncCompleted
        self.__eventsCache.onSyncStarted += self.__onSyncStarted
        g_playerEvents.onAccountBecomeNonPlayer += self.__onAccountBecomeNonPlayer
        self.__battleMattersController.onStateChanged += self.__onStateChanged
        self.__settingsCache.onSyncCompleted += self.__onSettingsSyncCompleted

    def __removeHintsListeners(self):
        self.__eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__eventsCache.onSyncStarted -= self.__onSyncStarted
        g_playerEvents.onAccountBecomeNonPlayer -= self.__onAccountBecomeNonPlayer
        self.__battleMattersController.onStateChanged -= self.__onStateChanged
        self.__settingsCache.onSyncCompleted -= self.__onSettingsSyncCompleted
        self.__hasHintListeners = False

    def __onDisconnected(self):
        self.__hints = self.__getDefaultHints(self.__battleMattersController)
        if not self.__hasHintListeners:
            self.__addHintsListeners()

    def __onAccountBecomeNonPlayer(self):
        self.__isSynced = False
        self.__stopHints()
        self.__eventsCache.onSyncCompleted += self.__onSyncCompleted
        self.__settingsCache.onSyncCompleted += self.__onSettingsSyncCompleted

    def __onSettingsSyncCompleted(self):
        self.__checkHints()
        self.__settingsCache.onSyncCompleted -= self.__onSettingsSyncCompleted

    def __onSyncCompleted(self):
        self.__isSynced = True
        self.__checkHints()
        self.__eventsCache.onSyncCompleted -= self.__onSyncCompleted

    def __checkHints(self):
        if self.__settingsCache.isSynced() and self.__isSynced:
            availableHints = []
            for hint in self.__hints:
                if hint.isShown():
                    hint.stop()
                availableHints.append(hint)

            self.__hints = availableHints
            if self.__hints:
                self.__startHints()
            else:
                self.__removeHintsListeners()

    def __onSyncStarted(self):
        self.__isSynced = False

    def __startHints(self):
        if self.__bmIsAvailable():
            for hint in self.__hints:
                hint.start()

    def __stopHints(self):
        for hint in self.__hints:
            hint.stop()

    def __onStateChanged(self):
        if self.__bmIsAvailable() and self.__isSynced:
            self.__startHints()
        else:
            self.__stopHints()

    def __bmIsAvailable(self):
        return self.__battleMattersController.isEnabled() and not self.__battleMattersController.isPaused()


class _BMManualTriggeredHint(object):
    _eventsCache = dependency.descriptor(IEventsCache)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _HINT_NAME = None
    __slots__ = ('_isStarted', '_battleMattersController', '_isHintVisible')

    def __init__(self, controller):
        super(_BMManualTriggeredHint, self).__init__()
        self._isStarted = False
        self._battleMattersController = controller
        self._isHintVisible = False

    def isShown(self):
        return bool(self._settingsCore.serverSettings.getOnceOnlyHintsSetting(self._HINT_NAME, default=False))

    def start(self):
        if not self._isStarted and self._canBeShownInFuture():
            self._onStart()
            self._isStarted = True

    def stop(self):
        if self._isStarted:
            self._onStop()
            self._isStarted = False
            self._isHintVisible = False

    def _onStart(self):
        raise NotImplementedError

    def _onStop(self):
        raise NotImplementedError

    def _show(self):
        self._isHintVisible = True

    def _hide(self):
        self._isHintVisible = False

    def _canBeShownInFuture(self):
        return not self.isShown()


class _FightBtnMultiShowHint(_BMManualTriggeredHint, IGlobalListener):
    _tutorialLoader = dependency.descriptor(ITutorialLoader)
    _CONTROL_NAME = 'FightButton'
    _HINT_NAME = OnceOnlyHints.BATTLE_MATTERS_FIGHT_BUTTON_HINT
    __slots__ = ('__fightBtnIsEnabled', '__waitingBattle')

    def __init__(self, controller):
        super(_FightBtnMultiShowHint, self).__init__(controller)
        self.__fightBtnIsEnabled = False
        self.__waitingBattle = False

    def onPrbEntitySwitched(self):
        if self.prbEntity.getQueueType() == QUEUE_TYPE.RANDOMS or self.__isDevBattle():
            g_playerEvents.onAvatarBecomePlayer += self.__onAvatarBecomePlayer
            self.__checkFightBtnHint()
            self.__waitingBattle = True
        else:
            self.__waitingBattle = False

    def _onStart(self):
        self.__waitingBattle = False
        if self._canBeShownInFuture():
            if not self.isShown():
                if self.prbDispatcher is None:
                    g_playerEvents.onPrbDispatcherCreated += self.__onPrbDispatcherCreated
                else:
                    self.startGlobalListening()
                if self.__checkFightBtnOnScene():
                    self.__setTriggers()
                    self.__fightBtnIsEnabled = self.__checkFightBtnIfAlreadyExist()
                    self.__checkFightBtnHint()
                else:
                    self.__addTutorialListeners()
        return

    def _onStop(self):
        if not self.__waitingBattle:
            g_playerEvents.onAvatarBecomePlayer -= self.__onAvatarBecomePlayer
        self._hide()
        self.stopGlobalListening()
        g_playerEvents.onPrbDispatcherCreated -= self.__onPrbDispatcherCreated
        self.__removeTutorialListeners()
        self.__resetTriggers()
        self.__fightBtnIsEnabled = False

    def _show(self):
        if not self._isHintVisible:
            self._tutorialLoader.gui.showInteractiveHint(self._CONTROL_NAME, {'updateRuntime': True}, [], False)
        super(_FightBtnMultiShowHint, self)._show()

    def _hide(self):
        if self._isHintVisible:
            self._tutorialLoader.gui.closeInteractiveHint(self._CONTROL_NAME)
        super(_FightBtnMultiShowHint, self)._hide()

    def _canBeShownInFuture(self):
        result = super(_FightBtnMultiShowHint, self)._canBeShownInFuture()
        if result:
            quests = self._battleMattersController.getRegularBattleMattersQuests()
            firstQuestIsNotCompleted = quests and not quests[0].isCompleted()
            result = result and firstQuestIsNotCompleted
        return result

    def __isDevBattle(self):
        return IS_DEVELOPMENT and self.prbEntity.getModeFlags() == FUNCTIONAL_FLAG.TRAINING

    def __setTriggers(self):
        self._tutorialLoader.gui.setTriggers(self._CONTROL_NAME, (TUTORIAL_TRIGGER_TYPES.ENABLED_CHANGE,))

    def __resetTriggers(self):
        self._tutorialLoader.gui.setTriggers(self._CONTROL_NAME, [])

    def __onAvatarBecomePlayer(self):
        if BigWorld.player().arenaBonusType in ARENA_BONUS_TYPE.RANDOM_RANGE:
            self._settingsCore.serverSettings.setOnceOnlyHintsSettings({self._HINT_NAME: True})
        self.__waitingBattle = False
        g_playerEvents.onAvatarBecomePlayer -= self.__onAvatarBecomePlayer

    def __addTutorialListeners(self):
        addListener = g_eventBus.addListener
        addListener(events.TutorialEvent.ON_COMPONENT_FOUND, self.__onItemFound, scope=EVENT_BUS_SCOPE.GLOBAL)
        addListener(events.TutorialEvent.ON_TRIGGER_ACTIVATED, self.__onTriggerActivated, scope=EVENT_BUS_SCOPE.GLOBAL)

    def __removeTutorialListeners(self):
        removeListener = g_eventBus.removeListener
        removeListener(events.TutorialEvent.ON_COMPONENT_FOUND, self.__onItemFound, scope=EVENT_BUS_SCOPE.GLOBAL)
        removeListener(events.TutorialEvent.ON_TRIGGER_ACTIVATED, self.__onTriggerActivated, scope=EVENT_BUS_SCOPE.GLOBAL)

    def __onItemFound(self, event):
        if event.targetID == self._CONTROL_NAME:
            self.__setTriggers()

    def __onTriggerActivated(self, event):
        if event.targetID == self._CONTROL_NAME:
            self.__fightBtnIsEnabled = event.componentState
            self.__checkFightBtnHint()

    def __onPrbDispatcherCreated(self):
        self.startGlobalListening()

    def __isReadyToShow(self):
        return self._canBeShownInFuture() and self.__fightBtnIsEnabled

    def __checkFightBtnOnScene(self):
        return self._CONTROL_NAME in self._tutorialLoader.gui.getFoundComponentsIDs()

    def __checkFightBtnHint(self):
        if self.prbEntity.getEntityFlags() != FUNCTIONAL_FLAG.UNDEFINED:
            if self.__isReadyToShow() and self.prbEntity.getQueueType() == QUEUE_TYPE.RANDOMS:
                self._show()
            elif self._canBeShownInFuture():
                self._hide()
            else:
                self.stop()

    def __checkFightBtnIfAlreadyExist(self):
        items = battle_selector_items.getItems()
        selected = items.update(self.prbDispatcher.getFunctionalState())
        return self.prbEntity.canPlayerDoAction().isValid and not selected.isLocked()


class _EntryPointHint(_BMManualTriggeredHint):
    _HINT_NAME = OnceOnlyHints.BATTLE_MATTERS_ENTRY_POINT_BUTTON_HINT
    __eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ()

    def _show(self):
        if not self._isHintVisible:
            getTutorialGlobalStorage().setValue(GLOBAL_FLAG.BATTLE_MATTERS_ENTRY_POINT, True)
        super(_EntryPointHint, self)._show()

    def _hide(self):
        if self._isHintVisible:
            getTutorialGlobalStorage().setValue(GLOBAL_FLAG.BATTLE_MATTERS_ENTRY_POINT, False)
        super(_EntryPointHint, self)._hide()

    def _onStart(self):
        if self.__isReadyToShow():
            self._show()
        else:
            self.__eventsCache.onSyncCompleted += self.__onSyncCompleted

    def _onStop(self):
        self._hide()
        self.__eventsCache.onSyncCompleted -= self.__onSyncCompleted

    def __onSyncCompleted(self):
        if self.__isReadyToShow():
            self._show()

    def __isReadyToShow(self):
        return len(self._battleMattersController.getCompletedBattleMattersQuests()) >= 1
