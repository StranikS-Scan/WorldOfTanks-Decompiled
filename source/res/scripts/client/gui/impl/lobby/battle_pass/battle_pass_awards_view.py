# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_awards_view.py
import SoundGroups
from battle_pass_common import BattlePassRewardReason, FinalReward
from frameworks.wulf import ViewSettings, WindowFlags, ViewStatus
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData, useBigAwardInjection
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator, createTooltipContentDecorator
from gui.battle_pass.battle_pass_helpers import getStyleInfoForChapter
from gui.battle_pass.sounds import BattlePassSounds
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_awards_view_model import BattlePassAwardsViewModel, RewardReason
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
MAP_REWARD_REASON = {BattlePassRewardReason.PURCHASE_BATTLE_PASS: RewardReason.BUY_BATTLE_PASS,
 BattlePassRewardReason.PURCHASE_BATTLE_PASS_LEVELS: RewardReason.BUY_BATTLE_PASS_LEVELS,
 BattlePassRewardReason.PURCHASE_BATTLE_PASS_WITH_LEVELS: RewardReason.BUY_BATTLE_PASS_WITH_LEVELS,
 BattlePassRewardReason.STYLE_UPGRADE: RewardReason.STYLE_UPGRADE,
 BattlePassRewardReason.PURCHASE_BATTLE_PASS_MULTIPLE: RewardReason.BUY_MULTIPLE_BATTLE_PASS,
 BattlePassRewardReason.SELECT_REWARD: RewardReason.BUY_BATTLE_PASS_LEVELS}
MAIN_REWARDS_LIMIT = 4
FINAL_REWARDS_LIMIT = 3
STANDART_REWARD_SIZE = 1
WIDE_REWARD_SIZE = 1.5
REWARD_SIZES = {'Standard': STANDART_REWARD_SIZE,
 'Wide': WIDE_REWARD_SIZE,
 'None': 0}

class BattlePassAwardsView(ViewImpl):
    __slots__ = ('__tooltipItems', '__closeCallback', '__needNotifyClosing', '__showBuyCallback')
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.battle_pass.BattlePassAwardsView())
        settings.model = BattlePassAwardsViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__tooltipItems = {}
        self.__closeCallback = None
        self.__showBuyCallback = None
        self.__needNotifyClosing = True
        super(BattlePassAwardsView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(BattlePassAwardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BattlePassAwardsView, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return None

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def _getEvents(self):
        return ((self.viewModel.onBuyClick, self.__onBuyClick),)

    def _onLoading(self, bonuses, packageBonuses, data, needNotifyClosing, *args, **kwargs):
        super(BattlePassAwardsView, self)._onLoading(*args, **kwargs)
        chapterID = data.get('chapter', 0)
        newLevel = data.get('newLevel', 0) or 0
        reason = data.get('reason', BattlePassRewardReason.DEFAULT)
        self.__closeCallback = data.get('callback')
        self.__showBuyCallback = data.get('showBuyCallback')
        isFinalReward = self.__battlePass.isFinalLevel(chapterID, newLevel) and reason not in (BattlePassRewardReason.PURCHASE_BATTLE_PASS, BattlePassRewardReason.PURCHASE_BATTLE_PASS_MULTIPLE, BattlePassRewardReason.SELECT_REWARD)
        isPurchase = reason in BattlePassRewardReason.PURCHASE_REASONS
        rewardReason = MAP_REWARD_REASON.get(reason, RewardReason.DEFAULT)
        isBattlePassPurchased = self.__battlePass.isBought(chapterID=chapterID) or isPurchase
        if chapterID and FinalReward.PROGRESSIVE_STYLE in self.__battlePass.getFreeFinalRewardTypes(chapterID):
            _, styleLevel = getStyleInfoForChapter(chapterID)
        else:
            styleLevel = None
        with self.viewModel.transaction() as tx:
            tx.setIsFinalReward(isFinalReward)
            tx.setReason(rewardReason)
            tx.setIsBattlePassPurchased(isBattlePassPurchased)
            tx.setCurrentLevel(newLevel)
            tx.setChapterID(chapterID)
            tx.setSeasonStopped(self.__battlePass.isPaused())
            tx.setIsBaseStyleLevel(styleLevel == 1)
            tx.setIsExtra(self.__battlePass.isExtraChapter(chapterID))
        if packageBonuses is not None and packageBonuses:
            self.__setPackageRewards(packageBonuses)
        self.__setAwards(bonuses, isFinalReward)
        isRewardSelected = reason == BattlePassRewardReason.SELECT_REWARD
        self.viewModel.setIsNeedToShowOffer(not (isBattlePassPurchased or isRewardSelected))
        switchHangarOverlaySoundFilter(on=True)
        SoundGroups.g_instance.playSound2D(BattlePassSounds.HOLIDAY_REWARD_SCREEN if self.__battlePass.isHoliday() else BattlePassSounds.REWARD_SCREEN)
        self.__needNotifyClosing = needNotifyClosing
        return

    def _onLoaded(self, data, *args, **kwargs):
        reason = data.get('reason', BattlePassRewardReason.DEFAULT)
        if reason in (BattlePassRewardReason.PURCHASE_BATTLE_PASS, BattlePassRewardReason.PURCHASE_BATTLE_PASS_LEVELS, BattlePassRewardReason.PURCHASE_BATTLE_PASS_WITH_LEVELS):
            g_eventBus.handleEvent(events.BattlePassEvent(events.BattlePassEvent.BUYING_THINGS), scope=EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        super(BattlePassAwardsView, self)._finalize()
        self.__tooltipItems = None
        switchHangarOverlaySoundFilter(on=False)
        if callable(self.__closeCallback):
            self.__closeCallback()
            self.__closeCallback = None
            self.__showBuyCallback = None
        if self.__needNotifyClosing:
            g_eventBus.handleEvent(events.BattlePassEvent(events.BattlePassEvent.AWARD_VIEW_CLOSE), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def __setAwards(self, bonuses, isFinalReward):
        rewards = BattlePassAwardsManager.composeBonuses(bonuses)
        rewards = BattlePassAwardsManager.sortBonuses(BattlePassAwardsManager.uniteTokenBonuses(rewards))
        if not rewards:
            return
        mainRewards = self.__setMainRewards(rewards, isFinalReward=isFinalReward)
        rewards = [ reward for reward in rewards if reward not in mainRewards ]
        packBonusModelAndTooltipData(rewards, self.viewModel.additionalRewards, self.__tooltipItems)

    def __setMainRewards(self, rewards, isFinalReward):
        limit = MAIN_REWARDS_LIMIT if not isFinalReward else FINAL_REWARDS_LIMIT
        mainRewards = []
        for reward in rewards:
            weight = self.__getRewardWeight(reward)
            if limit >= weight > 0:
                mainRewards.append(reward)
                limit -= weight
                if weight == WIDE_REWARD_SIZE:
                    self.viewModel.getWideRewardsIDs().addNumber(len(mainRewards) - 1)
            if limit <= 0:
                break

        with useBigAwardInjection():
            packBonusModelAndTooltipData(mainRewards, self.viewModel.mainRewards, self.__tooltipItems)
        return mainRewards

    @staticmethod
    def __getRewardWeight(bonus):
        return REWARD_SIZES.get(BattlePassAwardsManager.getBigIcon(bonus), 0)

    def __setPackageRewards(self, bonuses):
        composedBonuses = BattlePassAwardsManager.composeBonuses([bonuses])
        sortedBonuses = BattlePassAwardsManager.sortBonuses(BattlePassAwardsManager.uniteTokenBonuses(composedBonuses))
        packBonusModelAndTooltipData(sortedBonuses, self.viewModel.packageRewards, self.__tooltipItems)

    def __onBuyClick(self):
        if callable(self.__showBuyCallback):
            self.__showBuyCallback()
            self.__showBuyCallback = None
            self.__closeCallback = None
            if self.viewStatus not in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
                self.destroyWindow()
        return


class BattlePassAwardWindow(LobbyNotificationWindow):
    __slots__ = ('__params',)

    def __init__(self, bonuses, data, packageRewards=None, needNotifyClosing=True):
        self.__params = dict(bonuses=bonuses, packageBonuses=packageRewards, data=data, needNotifyClosing=needNotifyClosing)
        super(BattlePassAwardWindow, self).__init__(wndFlags=WindowFlags.SERVICE_WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BattlePassAwardsView(**self.__params))

    def isParamsEqual(self, *args, **kwargs):
        return all((pValue in args or kwargs.get(pName) == pValue for pName, pValue in self.__params.iteritems()))
