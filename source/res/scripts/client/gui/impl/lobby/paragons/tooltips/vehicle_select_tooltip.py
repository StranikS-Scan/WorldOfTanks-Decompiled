# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/tooltips/vehicle_select_tooltip.py
import adisp
from frameworks.wulf import ViewSettings
from gui.impl.lobby.paragons.paragons_helpers.paragons_model_helpers import fillParagonsVehicleModels
from helpers import dependency
from gui.impl.gen.view_models.views.lobby.paragons.tooltips.vehicle_select_tooltip_model import VehicleSelectTooltipModel
from gui.impl.pub import ViewImpl
from skeletons.gui.game_control import IParagonsRewardsShopController
from skeletons.gui.shared import IItemsCache

class VehicleSelectTooltip(ViewImpl):
    __slots__ = ()
    __rewardsCtrl = dependency.descriptor(IParagonsRewardsShopController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = VehicleSelectTooltipModel()
        super(VehicleSelectTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(VehicleSelectTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(VehicleSelectTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__fillRewardsVehicles(model.getVehicles())

    @adisp.adisp_process
    def __fillRewardsVehicles(self, vehList):
        _, res = yield self.__rewardsCtrl.getProducts()
        vehiclesCDs = []
        for info in res.itervalues():
            vehCD = info.get('vehicleCD')
            if vehCD:
                vehiclesCDs.append(vehCD)

        if vehiclesCDs:
            fillParagonsVehicleModels(vehList, vehiclesCDs)
