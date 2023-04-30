# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback/tooltips/main_reward_tooltip.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.winback.tooltips.main_reward_tooltip_model import MainRewardTooltipModel
from gui.impl.lobby.winback.winback_bonus_packer import getWinbackBonusPacker
from gui.impl.pub import ViewImpl
from gui.shared.missions.packers.bonus import packBonusModelAndTooltipData
if typing.TYPE_CHECKING:
    from typing import List
    from frameworks.wulf import Array
    from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel
    from gui.server_events.bonuses import SimpleBonus

class MainRewardTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.winback.tooltips.MainRewardTooltip(), model=MainRewardTooltipModel())
        settings.args = args
        settings.kwargs = kwargs
        super(MainRewardTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MainRewardTooltip, self).getViewModel()

    def _onLoading(self, rewards):
        super(MainRewardTooltip, self)._onLoading()
        with self.viewModel.getRewards().transaction() as tx:
            self.__updateRewards(tx, rewards)

    def __updateRewards(self, model, rewards):
        model.clear()
        packBonusModelAndTooltipData(rewards, getWinbackBonusPacker(), model)
