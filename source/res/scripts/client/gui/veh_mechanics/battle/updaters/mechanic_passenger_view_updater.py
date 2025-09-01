# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/mechanic_passenger_view_updater.py
from events_handler import eventHandler
from gui.battle_control.controllers.vehicle_passenger import hasVehiclePassengerCtrl
from gui.veh_mechanics.battle.updaters.updaters_common import VehicleMechanicUpdater

class IMechanicPassengerView(object):

    def setVisible(self, visible):
        raise NotImplementedError


class VehicleMechanicPassengerUpdater(VehicleMechanicUpdater):

    @eventHandler
    def onComponentDestroyed(self):
        self.__updateMechanicView(visible=False)
        super(VehicleMechanicPassengerUpdater, self).onComponentDestroyed()

    def _onVehiclePassengerUpdate(self, vehicle):
        super(VehicleMechanicPassengerUpdater, self)._onVehiclePassengerUpdate(vehicle)
        self.__updateMechanicView()

    @hasVehiclePassengerCtrl()
    def __updateMechanicView(self, visible=True, passengerCtrl=None):
        visibleForPassenger = visible and passengerCtrl.isCurrentVehicleAlive and passengerCtrl.isCurrentVehicleFPV
        self.view.setVisible(visibleForPassenger and self.mechanicComponent is not None)
        return
