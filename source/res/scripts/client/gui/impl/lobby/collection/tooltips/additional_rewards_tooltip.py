# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/collection/tooltips/additional_rewards_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.auxiliary.collections_helper import getCollectionsBonusPacker
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tooltips.additional_rewards_tooltip_model import AdditionalRewardsTooltipModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.pub import ViewImpl

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
            model.setHeaderText(R.invalid())
            model.setHeaderCount(0)
            model.setDescription(R.invalid())
            model.setDescriptionCount(0)
            bonusArray = model.getBonus()
            bonusArray.clear()
            packBonusModelAndTooltipData(bonuses, bonusArray, packer=getCollectionsBonusPacker())
            bonusArray.invalidate()
