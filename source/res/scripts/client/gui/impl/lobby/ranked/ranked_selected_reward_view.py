# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/ranked/ranked_selected_reward_view.py
import SoundGroups
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData, useBigAwardInjection
from gui.battle_pass.sounds import BattlePassSounds
from gui.impl.auxiliary.rewards_helper import getRewardTooltipContent
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.ranked.ranked_selected_reward_view_model import RankedSelectedRewardViewModel
from gui.impl.lobby.battle_pass.battle_pass_awards_view import REWARD_SIZES
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.ranked_battles.ranked_helpers.sound_manager import RankedSoundManager
MAIN_REWARDS_LIMIT = 3

class RankedSelectedRewardView(ViewImpl):
    __slots__ = ('__rewards', '__tooltipItems')

    def __init__(self, rewards):
        settings = ViewSettings(R.views.lobby.ranked.RankedSelectedRewardView())
        settings.model = RankedSelectedRewardViewModel()
        self.__rewards = rewards
        self.__tooltipItems = {}
        super(RankedSelectedRewardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RankedSelectedRewardView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(RankedSelectedRewardView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipData = self.__getBackportTooltipData(event)
        return getRewardTooltipContent(event, tooltipData)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def _onLoading(self, *args, **kwargs):
        super(RankedSelectedRewardView, self)._onLoading(*args, **kwargs)
        self.__setAwards()
        RankedSoundManager().setOverlayStateOn()
        SoundGroups.g_instance.playSound2D(BattlePassSounds.REWARD_SCREEN)

    def _finalize(self):
        super(RankedSelectedRewardView, self)._finalize()
        self.__tooltipItems = None
        RankedSoundManager().setOverlayStateOff()
        return

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            return self.__tooltipItems[tooltipId] if tooltipId in self.__tooltipItems else None

    def __setAwards(self):
        rewards = BattlePassAwardsManager.composeBonuses(self.__rewards)
        rewards = BattlePassAwardsManager.sortBonuses(BattlePassAwardsManager.uniteTokenBonuses(rewards))
        if not rewards:
            return
        mainRewards = self.__setMainRewards(rewards)
        rewards = [ reward for reward in rewards if reward not in mainRewards ]
        packBonusModelAndTooltipData(rewards, self.viewModel.additionalRewards, self.__tooltipItems)

    def __setMainRewards(self, rewards):
        limit = MAIN_REWARDS_LIMIT
        mainRewards = []
        for reward in rewards:
            weight = self.__getRewardWeight(reward)
            if limit >= weight > 0:
                mainRewards.append(reward)
                limit -= weight
            if limit <= 0:
                break

        with useBigAwardInjection():
            packBonusModelAndTooltipData(mainRewards, self.viewModel.mainRewards, self.__tooltipItems)
        return mainRewards

    @staticmethod
    def __getRewardWeight(bonus):
        return REWARD_SIZES.get(BattlePassAwardsManager.getBigIcon(bonus), 0)


class RankedSelectedRewardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, rewards):
        super(RankedSelectedRewardWindow, self).__init__(wndFlags=WindowFlags.SERVICE_WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=RankedSelectedRewardView(rewards), layer=WindowLayer.OVERLAY)
