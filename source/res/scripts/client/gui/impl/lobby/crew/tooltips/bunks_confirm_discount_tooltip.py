# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/bunks_confirm_discount_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.bunks_confirm_discount_tooltip_view_model import BunksConfirmDiscountTooltipViewModel
from gui.impl.pub import ViewImpl

class BunksConfirmDiscountTooltip(ViewImpl):
    __slots__ = ('__bunksCount', '__oldCost', '__newCost', '__isEnough')

    def __init__(self, bunksCount, oldCost, newCost, isEnough):
        self.__bunksCount = bunksCount
        self.__oldCost = oldCost
        self.__newCost = newCost
        self.__isEnough = isEnough
        settings = ViewSettings(R.views.lobby.crew.tooltips.BunksConfirmDiscountTooltip(), model=BunksConfirmDiscountTooltipViewModel())
        super(BunksConfirmDiscountTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BunksConfirmDiscountTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as vm:
            vm.setBunksCount(self.__bunksCount)
            vm.setOldCost(self.__oldCost)
            vm.setNewCost(self.__newCost)
            vm.setIsEnough(self.__isEnough)
