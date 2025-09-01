# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vehicle_passenger/passenger_interfaces.py
import typing
from gui.battle_control.controllers.interfaces import IBattleController
if typing.TYPE_CHECKING:
    from Event import LateEvent, Event

class IVehiclePassengerWatcher(object):

    @classmethod
    def getVehiclePassengerCtrl(cls):
        raise NotImplementedError


class IVehiclePassengerController(IBattleController):
    onVehiclePassengerUpdating = None
    onVehiclePassengerUpdate = None

    @property
    def isCurrentPlayerVehicle(self):
        raise NotImplementedError

    @property
    def isCurrentVehicleAlive(self):
        raise NotImplementedError

    @property
    def isCurrentVehicleFPV(self):
        raise NotImplementedError

    @property
    def currentVehicleID(self):
        raise NotImplementedError

    @property
    def playerVehicleID(self):
        raise NotImplementedError

    def setPlayerVehicle(self, vehicleID):
        raise NotImplementedError
