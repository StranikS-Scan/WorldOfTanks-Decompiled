# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/tooltips/vehicle_select_tooltip.py
import adisp
from frameworks.wulf import ViewSettings
from gui.impl.lobby.paragons.paragons_helpers.paragons_model_helpers import fillParagonsVehicleModels
from helpers import dependency
from gui.impl.gen.view_models.views.lobby.paragons.tooltips.vehicle_select_tooltip_model import VehicleSelectTooltipModel
from gui.impl.pub import ViewImpl
from skeletons.gui.game_control import IParagonsRewardsShopController, IParagonsController
from skeletons.gui.shared import IItemsCache

class VehicleSelectTooltip(ViewImpl):
    __slots__ = ('__level', '__chapterID', '__entitlementID')
    __rewardsCtrl = dependency.descriptor(IParagonsRewardsShopController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __paragonsCtrl = dependency.descriptor(IParagonsController)

    def __init__(self, level, chapterID, entitlementID, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = VehicleSelectTooltipModel()
        self.__level = level
        self.__chapterID = chapterID
        self.__entitlementID = entitlementID
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
        chapterLvl = self.__paragonsCtrl.paragons.getProgressByChapterID(self.__chapterID)
        self.viewModel.setIsAchieved(chapterLvl >= self.__level)
        vehiclesCDs = []
        _, products = yield self.__rewardsCtrl.getProducts()
        for _, product in products.iteritems():
            if not self.__rewardsCtrl.isValidProduct(product, self.__entitlementID):
                continue
            vehCD = product.get('vehicleCD')
            if vehCD:
                vehicle = self.__itemsCache.items.getItemByCD(vehCD)
                if not (vehicle.isInInventory or vehicle.isRestorePossible()):
                    vehiclesCDs.append(vehCD)

        if vehiclesCDs:
            fillParagonsVehicleModels(vehList, vehiclesCDs)
