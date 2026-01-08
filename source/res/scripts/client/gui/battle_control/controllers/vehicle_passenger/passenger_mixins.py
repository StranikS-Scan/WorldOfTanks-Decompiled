# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vehicle_passenger/passenger_mixins.py
from __future__ import absolute_import
import typing
from constants import UNKNOWN_VEHICLE_ID
from gui.battle_control.controllers.vehicle_passenger.passenger_interfaces import IVehiclePassengerWatcher
from gui.battle_control.controllers.vehicle_passenger.passenger_wrappers import hasVehiclePassengerCtrl
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.vehicle_passenger.passenger_interfaces import IVehiclePassengerController

class VehiclePassengerInfoWatcher(IVehiclePassengerWatcher):

    @classmethod
    def getVehiclePassengerCtrl(cls):
        return dependency.instance(IBattleSessionProvider).shared.vehiclePassenger

    @classmethod
    @hasVehiclePassengerCtrl(defReturn=UNKNOWN_VEHICLE_ID)
    def getVehiclePassengerCurrentVehicleID(cls, passengerCtrl=None):
        return passengerCtrl.currentVehicleID

    @classmethod
    @hasVehiclePassengerCtrl()
    def startVehiclePassengerLateListening(cls, updateListener, updatingListener=None, passengerCtrl=None):
        passengerCtrl.onVehiclePassengerUpdate.lateAdd(updateListener)
        if updatingListener is not None:
            passengerCtrl.onVehiclePassengerUpdating += updatingListener
        return

    @classmethod
    @hasVehiclePassengerCtrl()
    def startVehiclePassengerListening(cls, updateListener, updatingListener=None, passengerCtrl=None):
        passengerCtrl.onVehiclePassengerUpdate += updateListener
        if updatingListener is not None:
            passengerCtrl.onVehiclePassengerUpdating += updatingListener
        return

    @classmethod
    @hasVehiclePassengerCtrl()
    def stopVehiclePassengerListening(cls, updateListener, updatingListener=None, passengerCtrl=None):
        passengerCtrl.onVehiclePassengerUpdate -= updateListener
        if updatingListener is not None:
            passengerCtrl.onVehiclePassengerUpdating -= updatingListener
        return
