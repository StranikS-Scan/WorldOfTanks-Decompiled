# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/ls_vehicle_params_view.py
from gui.impl.lobby.hangar.sub_views.vehicle_params_view import CurrentVehicleParamsPresenter
from gui.shared.items_parameters import params_helper
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import AmmunitionSetupViewEvent
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class LSVehicleParamsPresenter(CurrentVehicleParamsPresenter):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(LSVehicleParamsPresenter, self).__init__()
        self._comparableVehicle = None
        return

    def _getVehicle(self):
        vehicle = super(LSVehicleParamsPresenter, self)._getVehicle()
        return self._removeConsumables(vehicle)

    def _getListeners(self):
        return ((AmmunitionSetupViewEvent.UPDATE_TTC, self._onUpdateTTC, EVENT_BUS_SCOPE.LOBBY),)

    def _finalize(self):
        self._comparableVehicle = None
        super(LSVehicleParamsPresenter, self)._finalize()
        return

    def _onUpdateTTC(self, event):
        self._comparableVehicle = self._removeConsumables(event.ctx.get('vehicleItem'))
        self.updateModel()

    def _getComparator(self):
        return params_helper.vehiclesComparator(self._comparableVehicle if self._comparableVehicle is not None else self._getVehicle(), self._getVehicle())

    def _isAdditionalValueEnabled(self):
        return True

    def _isExtraParamEnabled(self):
        return True

    def _removeConsumables(self, vehicle):
        vehicle = self.__itemsCache.items.getLayoutsVehicleCopy(vehicle)
        vehicle.consumables.setLayout(*([None] * len(vehicle.consumables.layout)))
        vehicle.consumables.setInstalled(*([None] * len(vehicle.consumables.installed)))
        return vehicle
