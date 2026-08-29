# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/mechanics/mechanic_passenger_updater.py
from __future__ import absolute_import
import typing
from events_handler import eventHandler
from gui.battle_control.controllers.vehicle_passenger import VehiclePassengerInfoWatcher, hasVehiclePassengerCtrl
from gui.veh_mechanics.battle.updaters.mechanics.mechanics_common import VehicleMechanicUpdater
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_constants import VehicleMechanic

class IMechanicPassengerView(object):

    def setVisibleForPassenger(self, visibleForPassenger):
        raise NotImplementedError


class VehicleMechanicPassengerUpdater(VehicleMechanicUpdater, VehiclePassengerInfoWatcher):

    def __init__(self, vehicleMechanic, view):
        super(VehicleMechanicPassengerUpdater, self).__init__(vehicleMechanic, view)
        self.__isVisibleForPassenger = None
        self.__hasMechanicComponent = None
        return

    @eventHandler
    def onMechanicComponentCatching(self, component):
        self.__hasMechanicComponent = True
        self.__updateMechanicView()

    @eventHandler
    def onMechanicComponentReleasing(self, component):
        self.__hasMechanicComponent = False
        self.__updateMechanicView()

    def initialize(self):
        super(VehicleMechanicPassengerUpdater, self).initialize()
        self.startVehiclePassengerLateListening(self.__onVehiclePassengerUpdate)

    def finalize(self):
        self.__isVisibleForPassenger = self.__hasMechanicComponent = None
        self.stopVehiclePassengerListening(self.__onVehiclePassengerUpdate)
        super(VehicleMechanicPassengerUpdater, self).finalize()
        return

    def __onVehiclePassengerUpdate(self, *_, **__):
        self.__updateMechanicView()

    @hasVehiclePassengerCtrl(defReturn=False)
    def __getVisibleByPassenger(self, passengerCtrl=None):
        return passengerCtrl.isCurrentVehicleAlive and passengerCtrl.isCurrentVehicleFPV

    def __updateMechanicView(self):
        visibleForPassenger = self.__hasMechanicComponent and self.__getVisibleByPassenger()
        if visibleForPassenger != self.__isVisibleForPassenger:
            self.__isVisibleForPassenger = visibleForPassenger
            self.view.setVisibleForPassenger(visibleForPassenger)
