# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/reward_compensation_tooltip.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.reward_compensation_tooltip_model import RewardCompensationTooltipModel
from gui.impl.pub import ViewImpl

class RewardCompensationTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.mono.battle_pass.tooltips.reward_compensation(), model=RewardCompensationTooltipModel(), args=args, kwargs=kwargs)
        super(RewardCompensationTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RewardCompensationTooltip, self).getViewModel()

    def _onLoading(self, initialBonus, compensationBonus, *args, **kwargs):
        with self.viewModel.transaction() as model:
            packBonusModelAndTooltipData([initialBonus], model.initialReward)
            packBonusModelAndTooltipData([compensationBonus], model.compensationReward)
