# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/ls_vehicle_params_view.py
from __future__ import absolute_import
from gui.impl.lobby.hangar.presenters.hangar_vehicle_params_presenter import HangarVehicleParamsPresenter
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class LSVehicleParamsPresenter(HangarVehicleParamsPresenter):
    __itemsCache = dependency.descriptor(IItemsCache)

    def _getVehicle(self):
        vehicle = super(LSVehicleParamsPresenter, self)._getVehicle()
        return self._removeConsumables(vehicle) if vehicle else None

    def _getDefaultVehicle(self):
        vehicle = super(LSVehicleParamsPresenter, self)._getVehicle()
        return self._removeConsumables(vehicle) if vehicle else None

    def _removeConsumables(self, vehicle):
        vehicle = self.__itemsCache.items.getLayoutsVehicleCopy(vehicle)
        vehicle.consumables.setLayout(*([None] * len(vehicle.consumables.layout)))
        vehicle.consumables.setInstalled(*([None] * len(vehicle.consumables.installed)))
        return vehicle
