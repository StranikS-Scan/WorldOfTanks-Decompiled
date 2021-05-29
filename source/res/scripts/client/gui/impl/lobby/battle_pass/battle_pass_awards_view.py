# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_awards_view.py
import SoundGroups
from battle_pass_common import BattlePassRewardReason
from frameworks.wulf import ViewSettings, WindowFlags
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData, useBigAwardInjection
from gui.battle_pass.battle_pass_decorators import createTooltipContentDecorator, createBackportTooltipDecorator
from gui.battle_pass.sounds import BattlePassSounds
from gui.battle_pass.battle_pass_helpers import BattlePassProgressionSubTabs, getStyleInfoForChapter
from gui.battle_pass.state_machine.state_machine_helpers import getStylesToChooseUntilChapter
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_awards_view_model import BattlePassAwardsViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.events_dispatcher import showMissionsBattlePassCommonProgression
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
MAP_REWARD_REASON = {BattlePassRewardReason.PURCHASE_BATTLE_PASS: BattlePassAwardsViewModel.BUY_BATTLE_PASS_REASON,
 BattlePassRewardReason.PURCHASE_BATTLE_PASS_LEVELS: BattlePassAwardsViewModel.BUY_BATTLE_PASS_LEVELS_REASON,
 BattlePassRewardReason.SELECT_TROPHY_DEVICE: BattlePassAwardsViewModel.SELECT_TROPHY_DEVICE_REASON,
 BattlePassRewardReason.SELECT_STYLE: BattlePassAwardsViewModel.SELECT_STYLE_REASON,
 BattlePassRewardReason.PURCHASE_BATTLE_PASS_MULTIPLE: BattlePassAwardsViewModel.BUY_MULTIPLE_BATTLE_PASS_REASON}
MAIN_REWARDS_LIMIT = 4
FINAL_REWARDS_LIMIT = 3
STANDART_REWARD_SIZE = 1
WIDE_REWARD_SIZE = 1.5
REWARD_SIZES = {'Standard': STANDART_REWARD_SIZE,
 'Wide': WIDE_REWARD_SIZE,
 'None': 0}

class BattlePassAwardsView(ViewImpl):
    __slots__ = ('__tooltipItems', '__closeCallback')
    __battlePassController = dependency.descriptor(IBattlePassController)

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = BattlePassAwardsViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__tooltipItems = {}
        self.__closeCallback = None
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

    def _onLoading(self, bonuses, data, *args, **kwargs):
        super(BattlePassAwardsView, self)._onLoading(*args, **kwargs)
        prevLevel = data.get('prevLevel', 0)
        prevChapter = self.__battlePassController.getChapterByLevel(prevLevel)
        newLevel = data.get('newLevel', 0)
        reason = data.get('reason', BattlePassRewardReason.DEFAULT)
        isFinalReward = self.__battlePassController.isFinalLevel(newLevel) and reason not in (BattlePassRewardReason.PURCHASE_BATTLE_PASS, BattlePassRewardReason.PURCHASE_BATTLE_PASS_MULTIPLE)
        self.__closeCallback = data.get('callback')
        isPurchase = reason in BattlePassRewardReason.PURCHASE_REASONS
        if reason in MAP_REWARD_REASON:
            reasonRewards = MAP_REWARD_REASON[reason]
        else:
            reasonRewards = self.viewModel.DEFAULT_REASON
        isBattlePassPurchased = self.__battlePassController.isBought(chapter=prevChapter) or isPurchase
        styleCD, level = getStyleInfoForChapter(prevChapter)
        self.viewModel.setIsFinalReward(isFinalReward)
        self.viewModel.setReason(reasonRewards)
        self.viewModel.setIsBattlePassPurchased(isBattlePassPurchased)
        self.viewModel.setIsNeedToShowOffer(not isBattlePassPurchased)
        self.viewModel.setPreviousLevel(prevLevel + 1)
        self.viewModel.setCurrentLevel(newLevel)
        self.viewModel.setIsBaseLevelStyle(True if level == 1 else False)
        self.viewModel.setChapterNumber(prevChapter)
        self.viewModel.setSeasonStopped(self.__battlePassController.isPaused())
        chapterTextKey = R.strings.battle_pass.chapter.name.num(prevChapter)
        if chapterTextKey.exists():
            self.viewModel.setChapter(backport.text(chapterTextKey()))
        self.viewModel.setIsStyleChosen(styleCD is not None)
        self.__setAwards(bonuses, isFinalReward)
        self.__addListeners()
        switchHangarOverlaySoundFilter(on=True)
        SoundGroups.g_instance.playSound2D(BattlePassSounds.REWARD_SCREEN)
        return

    def _onLoaded(self, data, *args, **kwargs):
        reason = data.get('reason', BattlePassRewardReason.DEFAULT)
        isPurchase = reason in (BattlePassRewardReason.PURCHASE_BATTLE_PASS, BattlePassRewardReason.PURCHASE_BATTLE_PASS_LEVELS)
        if isPurchase:
            g_eventBus.handleEvent(events.BattlePassEvent(events.BattlePassEvent.BUYING_THINGS), scope=EVENT_BUS_SCOPE.LOBBY)
        if callable(kwargs.get('callback')):
            kwargs.get('callback')()

    def _finalize(self):
        super(BattlePassAwardsView, self)._finalize()
        self.__removeListeners()
        self.__tooltipItems = None
        switchHangarOverlaySoundFilter(on=False)
        if self.__closeCallback is not None:
            self.__closeCallback()
        g_eventBus.handleEvent(events.BattlePassEvent(events.BattlePassEvent.AWARD_VIEW_CLOSE), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def _onBuyClick(self):
        showMissionsBattlePassCommonProgression(BattlePassProgressionSubTabs.BUY_TAB)
        self.destroyWindow()

    def __onStyleSelectClick(self, *_):
        chapter = self.viewModel.getChapterNumber()
        for style in getStylesToChooseUntilChapter(chapter + 1):
            self.__battlePassController.getRewardLogic().addStyleToChoose(style)

        self.destroyWindow()

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

    def __addListeners(self):
        model = self.viewModel
        model.onBuyClick += self._onBuyClick
        model.onStyleSelectClick += self.__onStyleSelectClick

    def __removeListeners(self):
        model = self.viewModel
        model.onBuyClick -= self._onBuyClick
        model.onStyleSelectClick -= self.__onStyleSelectClick


class BattlePassAwardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, bonuses, data, callback=None, wndFlags=None):
        if wndFlags is None:
            wndFlags = WindowFlags.SERVICE_WINDOW | WindowFlags.WINDOW_FULLSCREEN
        super(BattlePassAwardWindow, self).__init__(content=BattlePassAwardsView(R.views.lobby.battle_pass.BattlePassAwardsView(), bonuses=bonuses, data=data, callback=callback), wndFlags=wndFlags)
        return
