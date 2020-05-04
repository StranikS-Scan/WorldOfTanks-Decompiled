# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_awards_view.py
import SoundGroups
from battle_pass_common import BattlePassState, BattlePassRewardReason
from frameworks.wulf import ViewSettings, Array
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData, finalAwardsInjection
from gui.battle_pass.sounds import BattlePassSounds
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_awards_view_model import BattlePassAwardsViewModel
from gui.impl.pub import ViewImpl
from gui.server_events.events_dispatcher import showMissionsBattlePassCommonProgression
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE, event_dispatcher
from gui.shared.event_dispatcher import showBattlePassBuyWindow
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IBattlePassController

class BattlePassAwardsView(ViewImpl):
    __slots__ = ('__tooltipItems', '__closeCallback')
    __battlePassController = dependency.descriptor(IBattlePassController)

    def __init__(self, layoutID, wsFlags, viewModelClazz=BattlePassAwardsViewModel, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = wsFlags
        settings.model = viewModelClazz()
        settings.args = args
        settings.kwargs = kwargs
        self.__tooltipItems = {}
        self.__closeCallback = None
        super(BattlePassAwardsView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(BattlePassAwardsView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            tooltipData = self.__tooltipItems.get(tooltipId)
            if tooltipData is None:
                return
            window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
            window.load()
            return window
        else:
            return super(BattlePassAwardsView, self).createToolTip(event)

    def _onLoading(self, bonuses, data, *args, **kwargs):
        super(BattlePassAwardsView, self)._onLoading(*args, **kwargs)
        newState = data.get('newState', BattlePassState.BASE)
        prevLevel = data.get('prevLevel', 0)
        newLevel = data.get('newLevel', 0)
        reason = data.get('reason', BattlePassRewardReason.DEFAULT)
        callback = data.get('callback')
        isFinalReward = data.get('isFinalReward', False)
        if callback is not None:
            self.__closeCallback = callback
        if newLevel == 0 and newState == BattlePassState.POST:
            newLevel = self.__battlePassController.getMaxLevel()
        isPurchase = reason in (BattlePassRewardReason.PURCHASE_BATTLE_PASS, BattlePassRewardReason.PURCHASE_BATTLE_PASS_LEVELS)
        isPostProgression = BattlePassState.BASE != newState and not isFinalReward
        if reason == BattlePassRewardReason.PURCHASE_BATTLE_PASS:
            reasonRewards = self.viewModel.BUY_BATTLE_PASS_REASON
        elif reason == BattlePassRewardReason.PURCHASE_BATTLE_PASS_LEVELS:
            reasonRewards = self.viewModel.BUY_BATTLE_PASS_LEVELS_REASON
        else:
            reasonRewards = self.viewModel.DEFAULT_REASON
        self.viewModel.setIsFinalReward(isFinalReward)
        self.viewModel.setIsPostProgression(isPostProgression)
        self.viewModel.setReason(reasonRewards)
        self.viewModel.setIsBattlePassPurchased(self.__battlePassController.isBought() or isPurchase)
        self.viewModel.setPreviousLevel(prevLevel + 1)
        self.viewModel.setCurrentLevel(newLevel)
        self.viewModel.setMaxLevelBase(self.__battlePassController.getMaxLevel())
        self.viewModel.setMaxLevelPost(self.__battlePassController.getMaxLevel(False))
        if isPostProgression:
            self.__addBadgeInfo()
        self.__setAwards(bonuses, isPurchase, isFinalReward, isPostProgression)
        self.__addListeners()
        switchHangarOverlaySoundFilter(on=True)
        SoundGroups.g_instance.playSound2D(BattlePassSounds.REWARD_SCREEN)
        return

    def _onLoaded(self, data, *args, **kwargs):
        reason = data.get('reason', BattlePassRewardReason.DEFAULT)
        isPurchase = reason in (BattlePassRewardReason.PURCHASE_BATTLE_PASS, BattlePassRewardReason.PURCHASE_BATTLE_PASS_LEVELS)
        if isPurchase:
            g_eventBus.handleEvent(events.BattlePassEvent(events.BattlePassEvent.BUYING_THINGS), scope=EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        super(BattlePassAwardsView, self)._finalize()
        self.__removeListeners()
        self.__tooltipItems = None
        switchHangarOverlaySoundFilter(on=False)
        if self.__closeCallback is not None:
            self.__closeCallback()
            self.__closeCallback = None
        g_eventBus.handleEvent(events.BattlePassEvent(events.BattlePassEvent.AWARD_VIEW_CLOSE), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def _onBuyClick(self):
        self.destroyWindow()
        self.__showBuyWindow()

    @event_dispatcher.leaveEventMode
    def __showBuyWindow(self):
        showMissionsBattlePassCommonProgression()
        showBattlePassBuyWindow()

    def __setAwards(self, bonuses, isPremiumPurchase, isFinalReward, isPostProgression):
        rewards = BattlePassAwardsManager.composeBonuses(bonuses)
        if not rewards:
            return
        if isFinalReward:
            if self.__battlePassController.isBought():
                chosenRewards = [rewards[0], rewards[2]]
                boughtRewards = [rewards[1]]
                with finalAwardsInjection(self.__battlePassController.getAlternativeVoteOption()):
                    packBonusModelAndTooltipData(boughtRewards, self.viewModel.mainRewards, self.__tooltipItems)
                with finalAwardsInjection(self.__battlePassController.getVoteOption()):
                    packBonusModelAndTooltipData(chosenRewards, self.viewModel.mainRewards, self.__tooltipItems)
                rewards = rewards[3:]
            else:
                with finalAwardsInjection(self.__battlePassController.getVoteOption()):
                    packBonusModelAndTooltipData([rewards.pop(1)], self.viewModel.mainRewards, self.__tooltipItems)
                    packBonusModelAndTooltipData(rewards[:2], self.viewModel.mainRewards, self.__tooltipItems)
                rewards = rewards[2:]
        elif not isPremiumPurchase and not isPostProgression:
            packBonusModelAndTooltipData([rewards.pop(0)], self.viewModel.mainRewards, self.__tooltipItems)
        packBonusModelAndTooltipData(rewards, self.viewModel.additionalRewards, self.__tooltipItems)

    def __addBadgeInfo(self):
        badge = self.__battlePassController.getBadgeData()
        if badge is None:
            return
        else:
            tempStorage = Array()
            packBonusModelAndTooltipData([badge], tempStorage, self.__tooltipItems)
            self.viewModel.setBadgeTooltipId(first(self.__tooltipItems.keys()))
            return

    def __addListeners(self):
        model = self.viewModel
        model.onBuyClick += self._onBuyClick

    def __removeListeners(self):
        model = self.viewModel
        model.onBuyClick -= self._onBuyClick
