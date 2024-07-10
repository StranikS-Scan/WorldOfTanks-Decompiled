# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/additional_rewards_tooltip.py
from frameworks.wulf import ViewSettings
from frameworks.wulf.view.array import fillViewModelsArray
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tooltips.additional_rewards_tooltip_model import AdditionalRewardsTooltipModel
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

    def _onLoading(self, packedBonuses, *args, **kwargs):
        super(AdditionalRewardsTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setHeaderText(self._getHeader())
            model.setHeaderCount(0)
            model.setDescription(R.invalid())
            model.setDescriptionCount(0)
            fillViewModelsArray(packedBonuses, model.getBonus())

    @classmethod
    def _getHeader(cls):
        return R.strings.tooltips.quests.awards.additional.header()
