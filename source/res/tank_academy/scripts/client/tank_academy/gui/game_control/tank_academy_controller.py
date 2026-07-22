# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/game_control/tank_academy_controller.py
import typing
from ab_feature_test_token_based_shared import getGroupByFeature
from collections import OrderedDict
from constants import ARENA_BONUS_TYPE
from Event import EventManager, Event
from gui.Scaleform.daapi.view.lobby.hangar.entry_points.gf_header_widget import GFWidgetAliases
from gui.Scaleform.daapi.view.lobby.hangar.hangar_header import HangarHeader
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.server_events.bonuses import VehiclesBonus
from gui.server_events.event_items import ITankAcademyQuest
from helpers import dependency, server_settings
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IBootcampController, ITankAcademyController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from tank_academy.gui.game_control.tank_academy_hints_helper import TankAcademyHintsHelper
from tank_academy.helpers.server_settings import TankAcademyConfig
from tank_academy.gui.selectable_reward.selectable_reward_manager import TankAcademySelectableRewardManager
from tank_academy.gui.server_events.event_items import TankAcademyQuest, TankAcademyTokenQuest, TankAcademyGroup
from tank_academy.gui.server_events.events_helpers import isTankAcademyQuestID, isTankAcademyOfferToken, isTankAcademyDelayedRewardCurrencyToken
from tank_academy.gui.shared.event_dispatcher import showTankAcademyReward
from tank_academy_common.tank_academy_constants import GAME_PARAMS_KEY, TANK_ACADEMY_UNLOCK_TOKEN, TANK_ACADEMY_COMPLETE_TOKEN, AB_TEST_FEATURE_NAME, AB_TEST_DEFAULT_GROUP_NAME
if typing.TYPE_CHECKING:
    from typing import Optional, Union, List, Callable
    from gui.server_events.bonuses import SelectableBonus
    from gui.server_events.event_items import Quest, Group
_CLIENT_REWARD_IDX = -1

class TankAcademyController(ITankAcademyController):
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __connMgr = dependency.descriptor(IConnectionManager)
    __tankAcademySelectableRewardMgr = TankAcademySelectableRewardManager
    __bootcampController = dependency.descriptor(IBootcampController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ('_em', 'onStateChanged', 'onFinish', '_isEnabled', '_isAvailable', '__isWaitingToken', '__savedRewards', '__hasDelayedRewards', '__isFinished', '__abTestGroup', '__hangarWidgetAlias', '__suppressedPostBattleArenaUniqueIDs', '__hintsHelper')

    def __init__(self):
        super(TankAcademyController, self).__init__()
        self._em = EventManager()
        self.onStateChanged = Event(self._em)
        self.onFinish = Event(self._em)
        self._isEnabled = False
        self._isAvailable = False
        self.__savedRewards = {}
        self.__hasDelayedRewards = False
        self.__isFinished = False
        self.__isWaitingToken = False
        self.__abTestGroup = None
        self.__hangarWidgetAlias = None
        self.__suppressedPostBattleArenaUniqueIDs = set()
        self.__hintsHelper = None
        return

    def init(self):
        self.__addWidgetHandler()
        if self.__hintsHelper is None:
            self.__hintsHelper = TankAcademyHintsHelper(self)
        self.__connMgr.onConnected += self.__onConnected
        return

    def fini(self):
        self.__connMgr.onConnected -= self.__onConnected
        self._em.clear()
        self._isEnabled = False
        self.__savedRewards = None
        self.__removeWidgetHandler()
        if self.__hintsHelper:
            self.__hintsHelper.fini()
            self.__hintsHelper = None
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

    def isEnabled(self):
        return self._isEnabled

    def isFinished(self):
        return self.__itemsCache.items.tokens.getToken(TANK_ACADEMY_COMPLETE_TOKEN) is not None

    def isActive(self):
        return self.isEnabled() and (not self.isFinished() or self.hasUnobtainedDelayedRewards()) and self.isValidConfiguration()

    def isValidConfiguration(self):
        return len(self.getTankAcademyQuests()) > 0

    def hasUnobtainedDelayedRewards(self):
        return any((self.__isDelayedRewardCurrencyToken(t) for t in self.__itemsCache.items.tokens.getTokens().iterkeys()))

    def hasDelayedRewardsInQuest(self, quest):
        return quest.hasDelayedRewardBonus()

    def isFinalQuest(self, quest):
        return quest.getID() == self.getFinalQuest().getID()

    def getFinalQuest(self):
        quests = self.getTankAcademyQuests()
        return quests[-1] if quests else None

    def getFirstQuest(self):
        quests = self.getTankAcademyQuests()
        return quests[0] if quests else None

    def isTankAcademyQuestID(self, questID):
        return isTankAcademyQuestID(questID)

    def getQuestByIdx(self, questIdx):
        quests = self.getTankAcademyQuests()
        return quests[questIdx] if quests and len(quests) - 1 >= questIdx else None

    def getCompletedTankAcademyQuests(self):
        currentQuest = self.getCurrentQuest()
        currentQuestId = currentQuest.getOrder() if currentQuest else None

        def userFilterFunc(q):
            return q.isCompleted() and (currentQuestId is None or q.getOrder() < currentQuestId)

        return self.getTankAcademyQuests(userFilterFunc)

    def getCompletedTankAcademyQuestsCount(self):
        currentQuest = self.getCurrentQuest()
        return currentQuest.getOrder() - 1 if currentQuest else len(self.getCompletedTankAcademyQuests())

    def markPostBattleAutoShowSuppressed(self, arenaUniqueID):
        if arenaUniqueID:
            self.__suppressedPostBattleArenaUniqueIDs.add(arenaUniqueID)

    def consumePostBattleAutoShowSuppressed(self, arenaUniqueID):
        if arenaUniqueID in self.__suppressedPostBattleArenaUniqueIDs:
            self.__suppressedPostBattleArenaUniqueIDs.discard(arenaUniqueID)
            return True
        return False

    def getNotCompletedTankAcademyQuests(self):

        def userFilterFunc(q):
            return not q.isCompleted()

        return self.getTankAcademyQuests(userFilterFunc)

    def getTankAcademyQuestsByGroup(self, questGroup):

        def groupFilterFunc(q):
            return q.getGroupID() == questGroup.getID()

        return self.getTankAcademyQuests(groupFilterFunc)

    def getTankAcademyQuests(self, filterFunc=None):
        quests = self.__eventsCache.getHiddenQuests(self.__isTankAcademyQuestForThisPlayer).values()
        quests = sorted(quests, key=lambda q: q.getOrder())
        if filterFunc:
            return [ quest for quest in quests if filterFunc(quest) ]
        return quests

    def getTankAcademyQuestGroups(self, filterFunc=None):
        groups = self.__eventsCache.getGroups(self.__isTankAcademyGroupForThisPlayer).values()
        groups = sorted(groups, key=lambda g: g.getOrder())
        if filterFunc:
            return [ group for group in groups if filterFunc(group) ]
        return groups

    def getCountTankAcademyQuests(self):
        return len(self.getTankAcademyQuests())

    def isTAOfferToken(self, token):
        return isTankAcademyOfferToken(token)

    def isDelayedRewardToken(self, token):
        return self.isTAOfferToken(token)

    def hasOfferToken(self, offerToken):
        return False if not self.isTAOfferToken(offerToken) else self.__itemsCache.items.tokens.getToken(offerToken) is not None

    def hasDelayedRewardToken(self, offerToken):
        return self.hasOfferToken(offerToken)

    def isOfferRewardObtained(self, offerToken):
        return False if not self.isTAOfferToken(offerToken) else self.hasOfferToken(offerToken) and not self.__tankAcademySelectableRewardMgr.isAvailableBonus(offerToken)

    def isDelayedRewardObtained(self, offerToken):
        return self.isOfferRewardObtained(offerToken)

    def getOfferProperties(self, offerToken):
        if not self.isTAOfferToken(offerToken):
            return {}
        properties = self.__tankAcademySelectableRewardMgr.getRewardProperties(offerToken)
        return properties

    def getDelayedRewardCurrencyTokens(self):
        return [ t for t in self.__itemsCache.items.tokens.getTokens() if self.__isDelayedRewardCurrencyToken(t) ]

    def getVehicleOfferTokensWithUnobtainedGifts(self):
        return list(set((self.getOfferTokenByDelayedRewardCurrencyToken(delayedRewardCurrencyToken) for delayedRewardCurrencyToken in self.getDelayedRewardCurrencyTokens())))

    def getDelayedRewardExpirationTime(self):
        expirationTimes = [ self.__itemsCache.items.tokens.getTokenExpiryTime(t) for t in self.getDelayedRewardCurrencyTokens() ]
        return first(sorted(expirationTimes))

    def showAwardView(self, questsData, clientCtx=None):
        self.__saveRewards(questsData, clientCtx)
        rewardsOrder = sorted(self.__savedRewards.keys())
        for idx in rewardsOrder:
            showTankAcademyReward({idx: self.__savedRewards[idx]})
            self.__savedRewards.pop(idx)

    def getCurrentQuest(self):
        quests = self.getNotCompletedTankAcademyQuests()
        return quests[0] if quests else None

    def getQuestProgress(self, quest):
        currentProgress = 0
        maxProgress = 0
        if quest:
            items = quest.bonusCond.getConditions().items
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

    def getSelectedVehicle(self, offerToken):
        vehicle = None
        bonus = self.__getSelectableBonus(offerToken)
        if bonus:
            options = self.__tankAcademySelectableRewardMgr.getBonusReceivedOptions(bonus)
            for b, _ in options:
                if b.getName() == VehiclesBonus.VEHICLES_BONUS:
                    vehicle, _ = first(b.getVehicles())

        return vehicle

    def hasAccessToken(self):
        return self.__itemsCache.items.tokens.getToken(TANK_ACADEMY_UNLOCK_TOKEN) is not None

    def getABTestConfiguration(self):
        return self.__abTestGroup

    def getHangarWidgetAlias(self):
        return self.__hangarWidgetAlias

    def isFirstQuestCompleted(self):
        firstQuest = self.getFirstQuest()
        return firstQuest.isCompleted() if firstQuest else False

    def _getIsEnabled(self):
        isEnabled = self.__getConfig().isEnabled and not self.__bootcampController.isInBootcamp()
        return isEnabled and (self._isAvailable or self.__eventsCache.waitForSync or not self.__itemsCache.isSynced())

    def _onSyncCompleted(self):
        self.__update()

    def _onItemsCacheSync(self, *_, **__):
        previousIsAvailable = self._isAvailable
        self._isAvailable = self.hasAccessToken()
        if previousIsAvailable != self._isAvailable or self.__hasDelayedRewards or self.hasUnobtainedDelayedRewards():
            if self._isAvailable and self.__isWaitingToken:
                self.__isWaitingToken = False
                self.__eventsCache.onSyncCompleted += self._onSyncCompleted
                self.__lobbyContext.onServerSettingsChanged += self._onLobbyServerSettingChanged
                self.__lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        self.__update()

    def _onLobbyServerSettingChanged(self, newServerSettings):
        newServerSettings.onServerSettingsChange += self._onServerSettingsChange
        self.__update()

    @server_settings.serverSettingsChangeListener(GAME_PARAMS_KEY)
    def _onServerSettingsChange(self, _):
        self.__update()

    def _checkIsTankAcademyStateChanged(self):
        isEnabled = self._getIsEnabled()
        abTestGroup = self.__getABTestGroup()
        isChanged = isEnabled != self._isEnabled or self.__abTestGroup != abTestGroup
        if isChanged:
            self._isEnabled = isEnabled
            self.__abTestGroup = abTestGroup
            self.onStateChanged()
        return isChanged

    def __update(self):
        if self.__cachesAreReady():
            eventSent = self._checkIsTankAcademyStateChanged()
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
        hasUnobtainedDelayedRewards = self.hasUnobtainedDelayedRewards()
        if hasUnobtainedDelayedRewards != self.__hasDelayedRewards:
            self.__hasDelayedRewards = hasUnobtainedDelayedRewards
            if eventIsNeeded:
                self.onStateChanged()

    def __updateFinishState(self):
        newIsFinished = self.isFinished()
        if newIsFinished != self.__isFinished:
            self.__isFinished = newIsFinished
            if self.isFinished():
                self.onFinish()

    def __onConnected(self):
        self._isAvailable = False
        self.__savedRewards = OrderedDict()
        self.__hasDelayedRewards = False
        self.__isFinished = False
        self.__isWaitingToken = False
        self.__suppressedPostBattleArenaUniqueIDs.clear()
        self.__subscribe()
        if self.__cachesAreReady():
            self._checkIsTankAcademyStateChanged()

    def __onDisconnected(self):
        self.__unsubscribe()

    def __getSelectableBonus(self, offerToken):
        return first(self.__tankAcademySelectableRewardMgr.getSelectableBonuses(lambda t: t == offerToken))

    @classmethod
    def __getConfig(cls):
        return TankAcademyConfig(**cls.__lobbyContext.getServerSettings().getSettings().get(GAME_PARAMS_KEY))

    def __saveRewards(self, questsData, clientCtx=None):
        questsData = questsData or {}
        questIDs = questsData.get('completedQuestIDs', set())

        def filterFunc(quest):
            return quest.getID() in questIDs

        quests = self.getTankAcademyQuests(filterFunc)
        for questPosition, q in enumerate(quests):
            self.__savedRewards.setdefault(q.getOrder(), {'detailedRewards': questsData.get('detailedRewards', {}).get(q.getID(), {}),
             'isRewardScreenChain': len(quests) > 1,
             'isFirstRewardScreenChain': questPosition == 0})

        if clientCtx and VehiclesBonus.VEHICLES_BONUS in clientCtx:
            self.__savedRewards.setdefault(_CLIENT_REWARD_IDX, {'detailedRewards': {VehiclesBonus.VEHICLES_BONUS: clientCtx.get(VehiclesBonus.VEHICLES_BONUS, [])}})

    def __getABTestGroup(self):
        tokenNames = self.__itemsCache.items.tokens.getTokens().keys()
        group = getGroupByFeature(tokenNames, AB_TEST_FEATURE_NAME)
        return group if group else AB_TEST_DEFAULT_GROUP_NAME

    def __isDelayedRewardCurrencyToken(self, token):
        return isTankAcademyDelayedRewardCurrencyToken(token)

    @staticmethod
    def getOfferTokenByDelayedRewardCurrencyToken(delayedRewardCurrencyToken):
        return delayedRewardCurrencyToken.rsplit('_', 1)[0]

    def __isTankAcademyQuestForThisPlayer(self, quest):
        return quest.getABTestGroup() == self.__abTestGroup if isinstance(quest, (TankAcademyQuest, TankAcademyTokenQuest)) else False

    def __isTankAcademyGroupForThisPlayer(self, group):
        return group.getABTestGroup() == self.__abTestGroup if isinstance(group, TankAcademyGroup) else False

    def __addWidgetHandler(self):
        self.__hangarWidgetAlias = GFWidgetAliases(flashLinkage=HANGAR_ALIASES.GF_HEADER_WIDGET, registerAlias=HANGAR_ALIASES.TANK_ACADEMY_ENTRY_POINT)
        HangarHeader.addExternalWidgetHandler(self.__hangarWidgetAlias, self.__widgetHandler)

    def __widgetHandler(self, hangarHeader):
        return self.isActive() and hangarHeader.getCurrentArenaBonusType() == ARENA_BONUS_TYPE.REGULAR and self.isFirstQuestCompleted()

    def __removeWidgetHandler(self):
        HangarHeader.removeExternalWidgetHandler(self.__hangarWidgetAlias)
        self.__hangarWidgetAlias = None
        return
