# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/lobby/vehicles_carousel/tank_tooltip.py
from frameworks.wulf import ViewSettings
from frameworks.wulf.view.array import fillIntsArray
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Vehicle import getNationLessName
from races.gui.impl.gen.view_models.views.lobby.vehicles_carousel.tank_tooltip_model import TankTooltipModel

class TankTooltip(ViewImpl):
    __slots__ = ('_slotId', '_vehicle', '_inBattle', '_vehicleTth')

    def __init__(self, slotId, vehicle, inBattle, vehicleTth):
        settings = ViewSettings(layoutID=R.views.races.lobby.races_lobby_view.VehicleTooltip())
        settings.model = TankTooltipModel()
        super(TankTooltip, self).__init__(settings)
        self._slotId = slotId
        self._vehicle = vehicle
        self._inBattle = inBattle
        self._vehicleTth = vehicleTth

    @property
    def viewModel(self):
        return super(TankTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(TankTooltip, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setSlotId(self._slotId)
            model.setVehicleName(getNationLessName(self._vehicle.name))
            model.setVehicleUserName(self._vehicle.shortUserName)
            model.setDescription(self._vehicle.fullDescription)
            model.setInBattle(self._inBattle)
            fillIntsArray(self._vehicleTth, model.getVehicleTth())
