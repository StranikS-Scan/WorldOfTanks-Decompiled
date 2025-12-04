# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/new_year/tooltips/ny_selected_rewards_tooltip.py
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.selected_rewards_tooltip_model import SelectedRewardsTooltipModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Vehicle import getNationLessName
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from new_year.gui.shared.variadic_discount import VariadicDiscount

class SelectedRewardsTooltip(ViewImpl):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.new_year.lobby.new_year.tooltips.SelectedRewardsTooltip(), model=SelectedRewardsTooltipModel())
        settings.args = args
        settings.kwargs = kwargs
        super(SelectedRewardsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SelectedRewardsTooltip, self).getViewModel()

    def _onLoading(self, selectedRewards):
        super(SelectedRewardsTooltip, self)._onLoading()
        vmType = self.viewModel.getSelectedRewardsType()
        with self.viewModel.getSelectedRewards().transaction() as tx:
            tx.clear()
            for intCD, variadicID in selectedRewards:
                vehicle = self.__itemsCache.items.getItemByCD(int(intCD))
                discount = VariadicDiscount(variadicID)
                discount.getDiscountValue()
                vm = vmType()
                vm.setName(getNationLessName(vehicle.name))
                vm.setCreditDiscount(discount.getDiscountValue())
                vm.setUserName(vehicle.shortUserName)
                vm.setVehicleLvl(vehicle.level)
                vm.setNation(vehicle.nationName)
                tx.addViewModel(vm)
