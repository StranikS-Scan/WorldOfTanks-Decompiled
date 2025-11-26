# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/hangar/presenters/fun_random_vehicles_info_presenter.py
from __future__ import absolute_import
from gui.impl.lobby.common.presenters.vehicles_info_presenter import VehiclesInfoPresenter
from gui.shared.gui_items.Vehicle import Vehicle

class FunRandomVehiclesInfoPresenter(VehiclesInfoPresenter):

    def _toModelItem(self, vehicle):
        modelItem = super(FunRandomVehiclesInfoPresenter, self)._toModelItem(vehicle)
        modelItem['isSuitableVehicle'] = vehicle.getCustomState() != Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE
        return modelItem
