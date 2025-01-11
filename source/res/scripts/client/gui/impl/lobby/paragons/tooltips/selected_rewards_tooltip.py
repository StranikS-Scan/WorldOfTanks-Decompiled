# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/tooltips/selected_rewards_tooltip.py
from frameworks.wulf import ViewSettings
from frameworks.wulf.view.array import fillStringsArray
from gui.impl.gen.view_models.views.lobby.paragons.tooltips.selected_rewards_tooltip_model import SelectedRewardsTooltipModel
from gui.impl.pub import ViewImpl
from skeletons.gui.shared import IItemsCache
from helpers import dependency

class SelectedRewardsTooltip(ViewImpl):
    __slots__ = ('__selectedCDs',)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, selectedCDs, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = SelectedRewardsTooltipModel()
        self.__selectedCDs = selectedCDs or []
        super(SelectedRewardsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SelectedRewardsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as tx:
            rewardsModel = tx.getSelectedRewards()
            selectedVehicles = [ self.__getVehicleName(int(vehCD)) for vehCD in self.__selectedCDs ]
            fillStringsArray(selectedVehicles, rewardsModel)

    def __getVehicleName(self, vehCD):
        vehicle = self.__itemsCache.items.getItemByCD(vehCD)
        return vehicle.shortUserName
