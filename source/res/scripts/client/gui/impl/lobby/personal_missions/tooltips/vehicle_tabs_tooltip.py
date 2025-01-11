# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/tooltips/vehicle_tabs_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions.tooltips.vehicle_tabs_tooltip_model import VehicleTabsTooltipModel
from gui.impl.pub import ViewImpl

class VehicleTabsTooltip(ViewImpl):

    def __init__(self, maxVehicleLevel, minVehicleLevel, branchName):
        settings = ViewSettings(R.views.lobby.personal_missions.tooltips.VehicleTabsTooltip())
        settings.model = VehicleTabsTooltipModel()
        settings.args = (maxVehicleLevel, minVehicleLevel, branchName)
        super(VehicleTabsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(VehicleTabsTooltip, self).getViewModel()

    def _onLoading(self, maxVehicleLevel, minVehicleLevel, branchName, *args, **kwargs):
        super(VehicleTabsTooltip, self)._onLoading(*args, **kwargs)
        self.viewModel.setMaxVehicleLevel(maxVehicleLevel)
        self.viewModel.setMinVehicleLevel(minVehicleLevel)
        self.viewModel.setBranchName(branchName)
