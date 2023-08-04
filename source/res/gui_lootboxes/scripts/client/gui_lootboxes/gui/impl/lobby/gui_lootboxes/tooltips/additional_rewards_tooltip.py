# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/tooltips/additional_rewards_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tooltips.additional_rewards_tooltip_model import AdditionalRewardsTooltipModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.pub import ViewImpl
from gui_lootboxes.gui.bonuses.bonuses_packers import getRewardsBonusPacker

class AdditionalRewardsTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.tooltips.AdditionalRewardsTooltip())
        settings.model = AdditionalRewardsTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(AdditionalRewardsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AdditionalRewardsTooltip, self).getViewModel()

    def _onLoading(self, bonuses, *args, **kwargs):
        super(AdditionalRewardsTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setHeaderText(R.strings.gui_lootboxes.additionalRewardsTooltip.header())
            model.setHeaderCount(0)
            model.setDescription(R.invalid())
            model.setDescriptionCount(0)
            bonusArray = model.getBonus()
            packBonusModelAndTooltipData(bonuses, bonusArray, packer=getRewardsBonusPacker())
            bonusArray.invalidate()
