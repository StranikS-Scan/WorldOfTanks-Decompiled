# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/lobby/tank_academy/tooltips/additional_rewards_tooltip.py
from gui.impl.gen import R
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip as _AdditionalRewardsTooltip

class AdditionalRewardsTooltip(_AdditionalRewardsTooltip):

    def _onLoading(self, packedBonuses, *args, **kwargs):
        super(AdditionalRewardsTooltip, self)._onLoading(packedBonuses, *args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setHeaderText(R.strings.tank_academy.mainView.questRewards.box.tooltipHeader())
