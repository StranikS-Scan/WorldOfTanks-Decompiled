# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/weekly_reward_screen.py
from copy import copy
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.weekly_reward_screen_model import WeeklyRewardScreenModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import getNonQuestBonuses, splitBonuses, mergeBonuses
from gui.shared.bonuses_sorter import bonusesSortKeyFunc
from gui.shared.missions.packers.bonus import getDefaultBonusPacker
_MAX_MAIN_REWARDS = 3
_MAX_REWARDS = 10

class WeeklyRewardScreen(ViewImpl):
    __slots__ = ('__tooltipData', '__rawBonuses')

    def __init__(self, layoutID, bonuses):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = WeeklyRewardScreenModel()
        self.__tooltipData = {}
        self.__rawBonuses = copy(bonuses)
        super(WeeklyRewardScreen, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WeeklyRewardScreen, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(WeeklyRewardScreen, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            packedBonuses = self.viewModel.getRewards()[_MAX_REWARDS:]
            return AdditionalRewardsTooltip(packedBonuses)
        return super(WeeklyRewardScreen, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        index = event.getArgument('tooltipId')
        return self.__tooltipData.get(index, None)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),)

    def _onLoading(self, *args, **kwargs):
        super(WeeklyRewardScreen, self)._onLoading(*args, **kwargs)
        rewards = []
        for bonusType, bonusValue in self.__rawBonuses.items():
            bonus = getNonQuestBonuses(bonusType, bonusValue)
            rewards.extend(bonus)

        rewards = splitBonuses(mergeBonuses(rewards))
        rewards.sort(key=bonusesSortKeyFunc)
        mainRewards = rewards[:_MAX_MAIN_REWARDS]
        rewards = rewards[_MAX_MAIN_REWARDS:]
        if len(mainRewards) == _MAX_MAIN_REWARDS:
            mainRewards[0], mainRewards[1] = mainRewards[1], mainRewards[0]
        with self.viewModel.transaction() as model:
            packer = getDefaultBonusPacker()
            self.__fillRewardsModel(mainRewards, model.getMainRewards(), packer)
            self.__fillRewardsModel(rewards, model.getRewards(), packer)

    def __fillRewardsModel(self, rewards, rewardsList, packer):
        rewardsList.clear()
        packBonusModelAndTooltipData(rewards, rewardsList, self.__tooltipData, packer)
        rewardsList.invalidate()

    def __onClose(self):
        self.destroyWindow()


class WeeklyRewardScreenWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, bonuses=None, parent=None):
        super(WeeklyRewardScreenWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WeeklyRewardScreen(R.views.lobby.daily.WeeklyRewardScreen(), bonuses or {}), parent=parent)
