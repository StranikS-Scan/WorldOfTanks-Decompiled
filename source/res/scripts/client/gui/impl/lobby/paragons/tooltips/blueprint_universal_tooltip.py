# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/tooltips/blueprint_universal_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.paragons.tooltips.blueprint_universal_tooltip_model import BlueprintUniversalTooltipModel
from gui.impl.lobby.paragons.paragons_helpers.paragons_model_helpers import fillVehicleModel
from gui.impl.pub import ViewImpl
from gui.shared.tooltips import getUnlockPrice
from helpers import dependency
from skeletons.gui.game_control import IParagonsController
from skeletons.gui.shared import IItemsCache

class BlueprintUniversalTooltip(ViewImpl):
    __slots__ = ('__vehicleCD',)
    __paragonsController = dependency.descriptor(IParagonsController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicleCD):
        settings = ViewSettings(R.views.lobby.paragons.tooltips.BlueprintUniversalTooltip())
        settings.model = BlueprintUniversalTooltipModel()
        self.__vehicleCD = vehicleCD
        super(BlueprintUniversalTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BlueprintUniversalTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        blueprintsCount = self.__paragonsController.getVehicleResetBonusBlueprintsCount(self.__vehicleCD)
        vehicle = self.__itemsCache.items.getItemByCD(self.__vehicleCD)
        _, cost, _, _, discount = getUnlockPrice(vehicle.intCD, None, vehicle.level, blueprintsCount)
        with self.viewModel.transaction() as tx:
            tx.setBlueprintFragments(blueprintsCount)
            tx.setDiscount(discount)
            tx.setExperience(cost)
            fillVehicleModel(tx.vehicleInfo, vehicle)
        return
