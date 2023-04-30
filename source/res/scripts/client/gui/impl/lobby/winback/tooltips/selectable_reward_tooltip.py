# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback/tooltips/selectable_reward_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.winback.tooltips.selectable_reward_tooltip_model import SelectableRewardTooltipModel
from gui.impl.pub import ViewImpl

class SelectableRewardTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.winback.tooltips.SelectableRewardTooltip(), model=SelectableRewardTooltipModel())
        settings.args = args
        settings.kwargs = kwargs
        super(SelectableRewardTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SelectableRewardTooltip, self).getViewModel()

    def _onLoading(self, level, isDiscount, researchDiscount, purchaseDiscount):
        super(SelectableRewardTooltip, self)._onLoading()
        self.viewModel.setLevel(level)
        self.viewModel.setIsDiscount(isDiscount)
        self.viewModel.setResearchDiscount(researchDiscount)
        self.viewModel.setPurchaseDiscount(purchaseDiscount)
