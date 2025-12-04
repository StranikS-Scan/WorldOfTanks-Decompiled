# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/surprise_machine/robot_tv_rewards_view.py
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.surprise_machine.robot_tv_rewards_view_model import RobotTvRewardsViewModel
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, splitBonuses
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui_lootboxes.gui.bonuses.bonuses_packers import getRewardsBonusPacker
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from new_year.gui.shared.ny_machine_helper import stripOpenedLootboxTokens
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.gen import R

class RobotTvRewardsView(ViewImpl):
    __slots__ = ('__blur', '__tooltips')

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.new_year.lobby.new_year.RobotTvRewardsView(), flags=ViewFlags.VIEW, model=RobotTvRewardsViewModel())
        self.__blur = None
        self.__tooltips = {}
        super(RobotTvRewardsView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(RobotTvRewardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(RobotTvRewardsView, self).createToolTip(event)

    def getTooltipData(self, event):
        tID = event.getArgument('tooltipId')
        return self.__tooltips.get(tID, None)

    def setTokensUsed(self, count):
        self.viewModel.setTokensUsed(count)

    def fillRewards(self, rewardsListOfDicts):
        vmList = self.viewModel.getRewards()
        vmList.clear()
        rawBonuses = []
        for rewards in rewardsListOfDicts:
            if not rewards:
                continue
            cleaned = stripOpenedLootboxTokens(rewards)
            for bType, bVal in cleaned.iteritems():
                rawBonuses.extend(getNonQuestBonuses(bType, bVal))

        merged = splitBonuses(mergeBonuses(rawBonuses))
        self.__tooltips.clear()
        packBonusModelAndTooltipData(merged, vmList, tooltipData=self.__tooltips, packer=getRewardsBonusPacker())
        vmList.invalidate()

    def _initialize(self, *args, **kwargs):
        self.__blur = CachedBlur(enabled=True, ownLayer=self.getWindow().layer - 1)

    def _finalize(self):
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        return


class RobotTvRewardsViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(RobotTvRewardsViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=RobotTvRewardsView(), parent=parent)
