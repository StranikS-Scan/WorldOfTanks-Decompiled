# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/ls_vehicle_params_view.py
from gui.impl.lobby.hangar.sub_views.vehicle_params_view import VehicleParamsView
from gui.shared.items_parameters import params_helper
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AmmunitionSetupViewEvent

class LSVehicleParamsView(VehicleParamsView):

    def __init__(self, *args, **kwargs):
        super(LSVehicleParamsView, self).__init__(*args, **kwargs)
        self._comparableVehicle = None
        return

    def _getVehicle(self):
        vehicle = super(LSVehicleParamsView, self)._getVehicle()
        return self._removeConsumables(vehicle)

    def _subscribe(self):
        super(LSVehicleParamsView, self)._subscribe()
        g_eventBus.addListener(AmmunitionSetupViewEvent.UPDATE_TTC, self._onUpdateTTC, EVENT_BUS_SCOPE.LOBBY)

    def _unsubscribe(self):
        g_eventBus.removeListener(AmmunitionSetupViewEvent.UPDATE_TTC, self._onUpdateTTC, EVENT_BUS_SCOPE.LOBBY)
        super(LSVehicleParamsView, self)._unsubscribe()

    def _onUpdateTTC(self, event):
        self._comparableVehicle = self._removeConsumables(event.ctx.get('vehicleItem'))
        self.update()

    def _finalize(self):
        self._comparableVehicle = None
        super(LSVehicleParamsView, self)._finalize()
        return

    def _getComparator(self):
        return params_helper.vehiclesComparator(self._comparableVehicle if self._comparableVehicle is not None else self._getVehicle(), self._getVehicle())

    def _isAdditionalValueEnabled(self):
        return True

    def _isExtraParamEnabled(self):
        return True

    def _removeConsumables(self, vehicle):
        vehicle = self._itemsCache.items.getLayoutsVehicleCopy(vehicle)
        vehicle.consumables.setLayout(*([None] * len(vehicle.consumables.layout)))
        vehicle.consumables.setInstalled(*([None] * len(vehicle.consumables.installed)))
        return vehicle
