# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wot_anniversary/main_view.py
import logging
from typing import Dict, List, Optional, TYPE_CHECKING
import BigWorld
from constants import IS_CHINA
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.MissionsWotAnniversaryViewMeta import MissionsWotAnniversaryViewMeta
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.conditions.condition_group_model import ConditionGroupModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.daily_quests_model import DailyQuestsModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.login_quests_model import LoginQuestsModel, State as LoginQuestsState
from gui.impl.gen.view_models.views.lobby.wot_anniversary.main_view_model import MainViewModel, Phase as ModelPhase
from gui.impl.gen.view_models.views.lobby.wot_anniversary.mascot_quest_model import MascotQuestModel, State as MascotQuestsState
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.bonuses import splitBonuses
from gui.shared.event_dispatcher import showHangar, showBrowserOverlayView, showShop
from gui.shared.missions.packers.events import getEventUIDataPacker
from gui.shared.money import Currency
from gui.wot_anniversary.bonuses import getWotAnniversaryBonusPacker, packBonusModelAndTooltipDataFromQuests
from gui.wot_anniversary.tooltips.random_reward_tooltip import RandomRewardTooltip
from gui.wot_anniversary.utils import isTokenQuestUnlocked, getQuestNumber, getPhaseFromQuestID, isAnniversaryIntroShowed, showWotAnniversaryIntroWindow, isMascotQuestRewardAvailable
from gui.wot_anniversary.wot_anniversary_constants import WOT_ANNIVERSARY_LOGIN_UNLOCK_TOKEN, WOT_ANNIVERSARY_MASCOT_CLAIM_REWARD_TOKEN, WOT_ANNIVERSARY_MASCOT_TOKEN, WOT_ANNIVERSARY_LOGIN_CLAIM_REWARD_TOKEN, Phase as QuestPhase
from helpers import dependency
from shared_utils import findFirst, first
from skeletons.gui.game_control import IWalletController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.wot_anniversary import IWotAnniversaryController
from wg_async import AsyncScope, AsyncEvent, wg_async, wg_await, BrokenPromiseError, TimeoutError
from wot_anniversary_common import WotAnniversaryUrls
if TYPE_CHECKING:
    from frameworks.wulf import ViewEvent
    from gui.impl.backport import TooltipData
    from gui.impl.gen.view_models.common.missions.quest_model import QuestModel
_logger = logging.getLogger(__name__)
CLAIM_REWARD_TIMEOUT = 20
QUEST_TO_MODEL_PHASE = {QuestPhase.CAT: ModelPhase.CAT,
 QuestPhase.MOUSE: ModelPhase.MOUSE,
 QuestPhase.DEER: ModelPhase.DEER}
MASCOT_BONUS_ORDER = (Currency.EVENT_COIN,
 'style',
 'projection_decal',
 'decal',
 'customizations')

class WotAnniversaryMainComponent(InjectComponentAdaptor, MissionsWotAnniversaryViewMeta):
    __slots__ = ()

    def markVisited(self):
        pass

    def _makeInjectView(self):
        return MainView()


class MainView(ViewImpl):
    __wotAnniversaryCtrl = dependency.descriptor(IWotAnniversaryController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ('__tooltips', '__scope', '__selectRewardEvent', '__waitedCompleteQuestID')

    def __init__(self):
        settings = ViewSettings(R.views.lobby.wot_anniversary.MainView(), flags=ViewFlags.VIEW, model=MainViewModel())
        self.__tooltips = {}
        self.__scope = AsyncScope()
        self.__selectRewardEvent = AsyncEvent(scope=self.__scope)
        self.__waitedCompleteQuestID = None
        super(MainView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(MainView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(MainView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.wot_anniversary.tooltips.RandomRewardTooltip():
            tooltipData = self.getTooltipData(event)
            groupsData = tooltipData.specialArgs[0] if tooltipData and tooltipData.specialArgs else None
            return RandomRewardTooltip(groupsData)
        else:
            return super(MainView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onInfoPageOpen, self.__onOpenInfo),
         (self.viewModel.onGoToStore, self.__onOpenStore),
         (self.viewModel.loginQuests.claimReward, self.__onClaimLoginQuestRewards),
         (self.viewModel.mascotQuest.claimReward, self.__onClaimMascotQuestRewards),
         (self.__wotAnniversaryCtrl.onSettingsChanged, self.__onSettingsChanged),
         (self.__wallet.onWalletStatusChanged, self.__onWalletStatusChanged),
         (self.__eventsCache.onSyncCompleted, self.__onEventsCacheUpdated))

    def _getCallbacks(self):
        return (('stats.eventCoin', self.__onEventCoinUpdate),)

    def _onLoading(self, *args, **kwargs):
        super(MainView, self)._onLoading(*args, **kwargs)
        self.__tryOpenIntro()
        self.__updateModel()

    def _finalize(self):
        self.__scope.destroy()
        super(MainView, self)._finalize()

    def __updateModel(self):
        if not self.__wotAnniversaryCtrl.isAvailableAndActivePhase():
            return
        config = self.__wotAnniversaryCtrl.getConfig()
        self.__tooltips.clear()
        with self.viewModel.transaction() as tx:
            tx.setStartTime(config.startTime)
            tx.setEndTime(config.activePhaseEndTime)
            tx.setIsChina(IS_CHINA)
            self.__updateBalance(model=tx)
            self.__updateDailyQuests(model=tx.dailyQuests)
            self.__updateLoginQuests(model=tx.loginQuests)
            self.__updateMascotQuests(model=tx.mascotQuest)

    def __updateDailyQuests(self, model):
        quests = self.__wotAnniversaryCtrl.getDailyQuests().values()
        quests.sort(key=lambda q: (int(q.isCompleted()), getQuestNumber(q.getID())))
        anyQuest = first(quests)
        bonuses = anyQuest.getBonuses() if anyQuest else []
        bonus = findFirst(lambda b: b.getName() == 'eventCoin', bonuses)
        eventCoinCount = bonus.getValue() if bonus is not None else 0
        model.setEventCoinCount(eventCoinCount)
        questsModel = model.getQuests()
        questsModel.clear()
        for quest in quests:
            questUIPacker = getEventUIDataPacker(quest)
            fullQuestModel = questUIPacker.pack()
            questsModel.addViewModel(fullQuestModel)

        questsModel.invalidate()
        return

    def __updateLoginQuests(self, model):
        config = self.__wotAnniversaryCtrl.getConfig()
        quests = self.__wotAnniversaryCtrl.getLoginQuests().values()
        unlockedQuestStatuses = [ q.isCompleted() for q in quests if isTokenQuestUnlocked(q, WOT_ANNIVERSARY_LOGIN_UNLOCK_TOKEN) ]
        if not all(unlockedQuestStatuses):
            state = LoginQuestsState.CLAIM_REWARD
        elif len(unlockedQuestStatuses) == len(quests):
            state = LoginQuestsState.ALL_COMPLETED
        else:
            state = LoginQuestsState.WAIT_NEXT_DAY
        quests.sort(key=lambda q: getQuestNumber(q.getID()))
        model.setState(state)
        model.setEndDate(config.activePhaseEndTime)
        rewards = model.getRewards()
        rewards.clear()
        packBonusModelAndTooltipDataFromQuests(quests, rewards, self.__tooltips, packer=getWotAnniversaryBonusPacker())
        rewards.invalidate()

    def __updateMascotQuests(self, model):
        battleQuests = self.__wotAnniversaryCtrl.getMascotBattleQuests().values()
        rewardQuests = self.__wotAnniversaryCtrl.getMascotRewardQuests().values()
        if not battleQuests:
            _logger.error('Can not find any mascot battle quest.')
            return
        else:
            battleQuests.sort(key=lambda q: (int(q.isCompleted()), getQuestNumber(q.getID())))
            rewardQuests.sort(key=lambda q: q.getStartTime())
            activePhase = getPhaseFromQuestID(first(battleQuests).getID())
            anyBattleQuest = first(battleQuests)
            hasAvailableRewards = False
            notClaimedPreviousQuest = None
            activeRewardQuest = None
            previousPhase = None
            for quest in rewardQuests:
                phase = getPhaseFromQuestID(quest.getID())
                isQuestNotClaimed = isMascotQuestRewardAvailable(quest)
                hasAvailableRewards |= isQuestNotClaimed
                if phase != activePhase:
                    if isQuestNotClaimed:
                        previousPhase = phase
                        notClaimedPreviousQuest = quest
                activeRewardQuest = quest

            if activeRewardQuest is None:
                _logger.error('Can not find the active mascot reward quest.')
                return
            bonuses = None
            if notClaimedPreviousQuest is not None:
                state = MascotQuestsState.CLAIM_PREVIOUS_REWARD
                bonuses = notClaimedPreviousQuest.getBonuses()
            elif activeRewardQuest.isCompleted():
                if activeRewardQuest == rewardQuests[-1]:
                    state = MascotQuestsState.ALL_COMPLETED
                else:
                    state = MascotQuestsState.WAIT_NEXT_CYCLE
            elif hasAvailableRewards:
                state = MascotQuestsState.CLAIM_REWARD
            else:
                state = MascotQuestsState.IN_PROGRESS
            self.viewModel.setActivePhase(QUEST_TO_MODEL_PHASE.get(activePhase, ModelPhase.CAT))
            model.setActivePhase(QUEST_TO_MODEL_PHASE.get(previousPhase or activePhase, ModelPhase.CAT))
            model.setState(state)
            model.setCurrentProgress(len([ q for q in battleQuests if q.isCompleted() ]))
            model.setTotalProgress(len(battleQuests))
            model.setEndTime(int(anyBattleQuest.getFinishTime()))
            self.__clearQuestModelConditions(model.battle_quest)
            questUIPacker = getEventUIDataPacker(anyBattleQuest)
            questUIPacker.pack(model.battle_quest)
            rewards = model.getRewards()
            rewards.clear()
            bonuses = bonuses if bonuses is not None else activeRewardQuest.getBonuses()
            bonuses = splitBonuses(bonuses)
            bonuses.sort(key=self.__sortMascotBonusesKey)
            packBonusModelAndTooltipData(bonuses, rewards, self.__tooltips)
            rewards.invalidate()
            return

    @replaceNoneKwargsModel
    def __updateBalance(self, model=None):
        eventCoins = self.__itemsCache.items.stats.eventCoin if self.__wallet.isAvailable else -1
        model.setBalance(eventCoins)

    def __onClaimLoginQuestRewards(self):
        quests = self.__wotAnniversaryCtrl.getLoginQuests().values()
        notCompletedQuests = [ q for q in quests if isTokenQuestUnlocked(q, WOT_ANNIVERSARY_LOGIN_UNLOCK_TOKEN) and not q.isCompleted() ]
        if not notCompletedQuests:
            _logger.warning('Can not find any not completed login quest.')
            return
        self.__waitedCompleteQuestID = first(notCompletedQuests).getID()
        self.__showWaitingReward(WOT_ANNIVERSARY_LOGIN_CLAIM_REWARD_TOKEN)

    def __onClaimMascotQuestRewards(self):
        rewardQuests = self.__wotAnniversaryCtrl.getMascotRewardQuests().values()
        quest = findFirst(lambda q: isTokenQuestUnlocked(q, WOT_ANNIVERSARY_MASCOT_TOKEN.format(getPhaseFromQuestID(q.getID()))), rewardQuests)
        if quest is None:
            _logger.warning('Can not find any not completed mascot quest.')
            return
        else:
            self.__waitedCompleteQuestID = quest.getID()
            self.__showWaitingReward(WOT_ANNIVERSARY_MASCOT_CLAIM_REWARD_TOKEN)
            return

    @wg_async
    def __showWaitingReward(self, token):
        try:
            try:
                self.viewModel.loginQuests.setIsWaitingRewards(True)
                self.viewModel.mascotQuest.setIsWaitingRewards(True)
                BigWorld.player().requestSingleToken(token)
                yield wg_await(self.__selectRewardEvent.wait(), timeout=CLAIM_REWARD_TIMEOUT)
            except TimeoutError:
                _logger.warning('Timeout Error during the claiming of reward')
            except BrokenPromiseError:
                _logger.info('%s has been destroyed before claiming of reward completed', self)

        finally:
            self.__waitedCompleteQuestID = None
            self.__selectRewardEvent.clear()
            if self.viewModel is not None:
                self.viewModel.loginQuests.setIsWaitingRewards(False)
                self.viewModel.mascotQuest.setIsWaitingRewards(False)

        return

    @staticmethod
    def __tryOpenIntro():
        if not isAnniversaryIntroShowed():
            showWotAnniversaryIntroWindow()

    @staticmethod
    def __onClose():
        showHangar()

    def __onOpenInfo(self):
        url = self.__wotAnniversaryCtrl.getUrl(WotAnniversaryUrls.INFO_PAGE)
        if url is None:
            _logger.error('Wot Anniversary info page is missed.')
            return
        else:
            showBrowserOverlayView(url, alias=VIEW_ALIAS.BROWSER_OVERLAY, parent=self.getParentWindow())
            return

    def __onOpenStore(self):
        url = self.__wotAnniversaryCtrl.getUrl(WotAnniversaryUrls.SHOP_EVENT_PATH)
        if url is None:
            _logger.error('Wot Anniversary shop path is missed.')
            return
        else:
            showShop(path=url)
            return

    def __onEventCoinUpdate(self, _):
        self.__updateModel()

    def __onWalletStatusChanged(self, _):
        self.__updateBalance()

    def __onBalanceChanged(self, _):
        self.__updateBalance()

    def __onEventsCacheUpdated(self):
        if self.__waitedCompleteQuestID is not None and not self.__selectRewardEvent.is_set():
            quest = first(self.__eventsCache.getHiddenQuests(lambda q: q.getID() == self.__waitedCompleteQuestID).values())
            if quest is not None and quest.isCompleted():
                self.__selectRewardEvent.set()
        self.__updateModel()
        return

    def __onSettingsChanged(self):
        if not self.__wotAnniversaryCtrl.isAvailableAndActivePhase():
            showHangar()

    @staticmethod
    def __sortMascotBonusesKey(bonus):
        bonusName = bonus.getName()
        if bonusName in MASCOT_BONUS_ORDER:
            if bonusName == 'customizations':
                customization = first(bonus.getCustomizations())
                if customization is not None:
                    bonusName = customization.get('custType')
                    bonusName = bonusName if bonusName in MASCOT_BONUS_ORDER else 'customizations'
            return MASCOT_BONUS_ORDER.index(bonusName)
        else:
            return len(MASCOT_BONUS_ORDER) + 1

    @staticmethod
    def __clearQuestModelConditions(questModel):
        for conditions in (questModel.bonusCondition, questModel.postBattleCondition, questModel.preBattleCondition):
            if isinstance(conditions, ConditionGroupModel):
                array = conditions.getItems()
                array.clear()
                array.invalidate()
