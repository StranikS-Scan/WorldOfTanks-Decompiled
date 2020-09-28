# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_awards_view.py
import SoundGroups
from battle_pass_common import BattlePassState, BattlePassRewardReason
from frameworks.wulf import ViewSettings, Array, WindowFlags, ViewFlags
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData, finalAwardsInjection
from gui.battle_pass.sounds import BattlePassSounds
from gui.battle_pass.battle_pass_helpers import BattlePassProgressionSubTabs, showOfferByBonusName
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_awards_view_model import BattlePassAwardsViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.events_dispatcher import showMissionsBattlePassCommonProgression
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IBattlePassController
MAP_REWARD_REASON = {BattlePassRewardReason.PURCHASE_BATTLE_PASS: BattlePassAwardsViewModel.BUY_BATTLE_PASS_REASON,
 BattlePassRewardReason.PURCHASE_BATTLE_PASS_LEVELS: BattlePassAwardsViewModel.BUY_BATTLE_PASS_LEVELS_REASON,
 BattlePassRewardReason.SELECT_TROPHY_DEVICE: BattlePassAwardsViewModel.SELECT_TROPHY_DEVICE_REASON}
MAIN_REWARDS_LIMIT = 4
STANDART_REWARD_SIZE = 1
WIDE_REWARD_SIZE = 1.5
REWARD_SIZES = {'Standard': STANDART_REWARD_SIZE,
 'Wide': WIDE_REWARD_SIZE,
 'None': 0}

class BattlePassAwardsView(ViewImpl):
    __slots__ = ('__tooltipItems',)
    __battlePassController = dependency.descriptor(IBattlePassController)

    def __init__(self, layoutID, wsFlags, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = wsFlags
        settings.model = BattlePassAwardsViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__tooltipItems = {}
        super(BattlePassAwardsView, self).__init__(settings)

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
        isFinalReward = data.get('isFinalReward', False)
        if newLevel == 0 and newState == BattlePassState.POST:
            newLevel = self.__battlePassController.getMaxLevel()
        isPurchase = reason in (BattlePassRewardReason.PURCHASE_BATTLE_PASS, BattlePassRewardReason.PURCHASE_BATTLE_PASS_LEVELS)
        isPostProgression = BattlePassState.BASE != newState and not isFinalReward
        if reason in MAP_REWARD_REASON:
            reasonRewards = MAP_REWARD_REASON[reason]
        else:
            reasonRewards = self.viewModel.DEFAULT_REASON
        isBattlePassPurchased = self.__battlePassController.isBought() or isPurchase
        self.viewModel.setIsFinalReward(isFinalReward)
        self.viewModel.setIsPostProgression(isPostProgression)
        self.viewModel.setReason(reasonRewards)
        self.viewModel.setIsBattlePassPurchased(isBattlePassPurchased)
        self.viewModel.setIsNeedToShowOffer(not isBattlePassPurchased and not self.__battlePassController.isPlayerNewcomer())
        self.viewModel.setPreviousLevel(prevLevel + 1)
        self.viewModel.setCurrentLevel(newLevel)
        self.viewModel.setMaxLevelBase(self.__battlePassController.getMaxLevel())
        self.viewModel.setMaxLevelPost(self.__battlePassController.getMaxLevel(False))
        self.viewModel.setIsChooseDeviceEnabled(self.__battlePassController.isChooseDeviceEnabled())
        if isPostProgression:
            self.__addBadgeInfo()
        self.__setAwards(bonuses, isFinalReward)
        self.__addListeners()
        switchHangarOverlaySoundFilter(on=True)
        SoundGroups.g_instance.playSound2D(BattlePassSounds.REWARD_SCREEN)

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
        self.__battlePassController.getFinalRewardLogic().postEscape()
        g_eventBus.handleEvent(events.BattlePassEvent(events.BattlePassEvent.AWARD_VIEW_CLOSE), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def _onBuyClick(self):
        showMissionsBattlePassCommonProgression(BattlePassProgressionSubTabs.BUY_TAB)
        self.destroyWindow()

    def __onDeviceSelectClick(self, kwargs):
        showOfferByBonusName(kwargs.get('rewardName'))
        self.destroyWindow()

    def __setAwards(self, bonuses, isFinalReward):
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
        else:
            self.__extractBadgeReward(rewards)
            mainRewards = self.__setMainRewards(rewards)
            rewards = rewards[len(mainRewards):]
        packBonusModelAndTooltipData(rewards, self.viewModel.additionalRewards, self.__tooltipItems)

    def __setMainRewards(self, rewards):
        limit = MAIN_REWARDS_LIMIT
        mainRewards = []
        for reward in rewards:
            weight = self.__getRewardWeight(reward)
            if limit >= weight > 0:
                mainRewards.append(reward)
                limit -= weight
                if weight == WIDE_REWARD_SIZE:
                    self.viewModel.getWideRewardsIDs().addNumber(len(mainRewards) - 1)
            break

        for reward in mainRewards:
            value = reward.getValue()
            if reward.getName() == 'customizations':
                altVoteOption = self.__battlePassController.getAlternativeVoteOption()
                if value[0]['custType'] == 'projection_decal':
                    with finalAwardsInjection(value[0]['id']):
                        packBonusModelAndTooltipData([reward], self.viewModel.mainRewards, self.__tooltipItems)
                elif value[0]['custType'] == 'style' and altVoteOption != 0:
                    with finalAwardsInjection(altVoteOption):
                        packBonusModelAndTooltipData([reward], self.viewModel.mainRewards, self.__tooltipItems)
                elif value[0]['custType'] == 'decal':
                    with finalAwardsInjection(value[0]['id']):
                        packBonusModelAndTooltipData([reward], self.viewModel.mainRewards, self.__tooltipItems)
                else:
                    packBonusModelAndTooltipData([reward], self.viewModel.mainRewards, self.__tooltipItems)
            packBonusModelAndTooltipData([reward], self.viewModel.mainRewards, self.__tooltipItems)

        return mainRewards

    @staticmethod
    def __getRewardWeight(bonus):
        return REWARD_SIZES.get(BattlePassAwardsManager.getBigIcon(bonus), 0)

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
        model.onDeviceSelectClick += self.__onDeviceSelectClick

    def __removeListeners(self):
        model = self.viewModel
        model.onBuyClick -= self._onBuyClick
        model.onDeviceSelectClick -= self.__onDeviceSelectClick

    def __extractBadgeReward(self, rewards):
        for bonus in rewards:
            if bonus.getName() != 'dossier':
                continue
            if bonus.getBadges():
                rewards.remove(bonus)


class BattlePassAwardWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, bonuses, data):
        super(BattlePassAwardWindow, self).__init__(content=BattlePassAwardsView(R.views.lobby.battle_pass.BattlePassAwardsView(), wsFlags=ViewFlags.OVERLAY_VIEW, bonuses=bonuses, data=data), wndFlags=WindowFlags.OVERLAY, decorator=None)
        return
