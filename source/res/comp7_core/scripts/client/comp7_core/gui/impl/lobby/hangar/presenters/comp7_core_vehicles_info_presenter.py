# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/impl/lobby/hangar/presenters/comp7_core_vehicles_info_presenter.py
import typing
from gui.impl.lobby.hangar.presenters.vehicles_info_presenter import VehiclesInfoPresenter
if typing.TYPE_CHECKING:
    from gui.shared.gui_items import Vehicle

class Comp7CoreVehiclesInfoPresenter(VehiclesInfoPresenter):

    @property
    def _modeController(self):
        return NotImplementedError

    def _toModelItem(self, vehicle):
        modelItem = super(Comp7CoreVehiclesInfoPresenter, self)._toModelItem(vehicle)
        modelItem['isSuitableVehicle'] = self._modeController.isSuitableVehicle(vehicle) is None
        return modelItem
