# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/fort_rush_reward_view.py
from __future__ import absolute_import
import typing
from fort_rush.gui.impl.gen.view_models.views.lobby.fort_rush_rewards_screen_view_model import FortRushRewardsScreenViewModel
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.server_events.bonuses import getNonQuestBonuses
from helpers import dependency
from frameworks.wulf import ViewFlags
from gui.shared.missions.packers.bonus import getDefaultBonusPacker
if typing.TYPE_CHECKING:
    from typing import Any
    from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel
    from frameworks.wulf import Array
    from gui.shared.missions.packers.bonus import BonusUIPacker

class FortRushRewardView(ViewImpl):
    __ctrl = dependency.descriptor(IFortRushBattleController)

    def __init__(self, ctx):
        layoutID = R.views.fort_rush.mono.lobby.reward_screen()
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = FortRushRewardsScreenViewModel()
        super(FortRushRewardView, self).__init__(settings)
        self.__tooltips = {}
        self.__rewardData = ctx['rewardData']

    @property
    def viewModel(self):
        return self.getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(FortRushRewardView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    def _onLoading(self, *args, **kwargs):
        super(FortRushRewardView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            vm.setIsCompleted(self.__ctrl.isProgressionCompleted())
            bonusPacker = getDefaultBonusPacker()
            self.__tooltips = {}
            self.__packRewards(vm.getRewards(), self.__rewardData, bonusPacker)

    def _finalize(self):
        self.__tooltips = {}
        super(FortRushRewardView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onCloseClick),)

    def __onCloseClick(self):
        self.destroyWindow()

    def __packRewards(self, rewardsModel, rewards, packer):
        rawDataBonuses = []
        for k, v in rewards:
            rawDataBonuses.extend(getNonQuestBonuses(k, v))

        packBonusModelAndTooltipData(rawDataBonuses, rewardsModel, tooltipData=self.__tooltips, packer=packer)
