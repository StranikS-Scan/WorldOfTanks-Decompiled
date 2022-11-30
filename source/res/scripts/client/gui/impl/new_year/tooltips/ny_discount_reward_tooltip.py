# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/ny_discount_reward_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_discount_reward_tooltip_model import NyDiscountRewardTooltipModel
from new_year.variadic_discount import VariadicDiscount

class NyDiscountRewardTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyDiscountRewardTooltip())
        settings.model = NyDiscountRewardTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyDiscountRewardTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyDiscountRewardTooltip, self).getViewModel()

    def _initialize(self, variadicID, discount, rewardLevel):
        variadicDiscount = VariadicDiscount(variadicID)
        with self.viewModel.transaction() as tx:
            tx.setLevel(variadicDiscount.getTankLevel())
            tx.setDiscount(discount)
            tx.setQuestsCount(rewardLevel)
            selectedVehicle = variadicDiscount.getSelectedVehicle()
            if selectedVehicle:
                tx.setSelectedVehicle(selectedVehicle.userName)
