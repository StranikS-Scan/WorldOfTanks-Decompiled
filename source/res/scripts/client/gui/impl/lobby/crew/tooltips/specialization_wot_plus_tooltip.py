# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/specialization_wot_plus_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.specialization_wot_plus_tooltip_model import SpecializationWotPlusTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class SpecializationWotPlusTooltip(ViewImpl):
    __slots__ = ('vehicleCD',)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicleCD, layoutID=R.views.lobby.crew.tooltips.SpecializationWotPlusTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = SpecializationWotPlusTooltipModel()
        super(SpecializationWotPlusTooltip, self).__init__(settings)
        self.vehicleCD = vehicleCD

    @property
    def viewModel(self):
        return super(SpecializationWotPlusTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(SpecializationWotPlusTooltip, self)._onLoading()
        vehicle = self._itemsCache.items.getItemByCD(self.vehicleCD)
        with self.viewModel.transaction() as model:
            model.vehicle.setVehicleLvl(vehicle.level)
            model.vehicle.setVehicleType(vehicle.type)
            model.vehicle.setVehicleName(vehicle.userName)
