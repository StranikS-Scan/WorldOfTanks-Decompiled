# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vehicle_passenger/passenger_ctrl.py
import typing
import weakref
import Event
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, VEHICLE_VIEW_STATE, UNKNOWN_VEHICLE_ID
from gui.battle_control.controllers.vehicle_passenger.passenger_interfaces import IVehiclePassengerController
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.vehicle_state_ctrl import VehicleStateController
    from Vehicle import Vehicle

class VehiclePassengerController(IVehiclePassengerController):
    __slots__ = ('__playerVehicleID', '__isCurrentVehicleAlive', '__isCurrentVehicleFPV', '__vehStateCtrl', '__eManager', 'onVehiclePassengerUpdating', 'onVehiclePassengerUpdate')

    def __init__(self, vehStateCtrl):
        self.__vehStateCtrl = weakref.proxy(vehStateCtrl)
        self.__playerVehicleID = UNKNOWN_VEHICLE_ID
        self.__isCurrentVehicleAlive = False
        self.__isCurrentVehicleFPV = False
        self.__eManager = Event.EventManager()
        self.onVehiclePassengerUpdating = Event.Event(self.__eManager)
        self.onVehiclePassengerUpdate = Event.LateEvent(self.__latePassengerUpdate, self.__eManager)

    @property
    def isCurrentPlayerVehicle(self):
        return self.__playerVehicleID == self.currentVehicleID

    @property
    def isCurrentVehicleAlive(self):
        return self.__isCurrentVehicleAlive

    @property
    def isCurrentVehicleFPV(self):
        return self.__isCurrentVehicleFPV or self.isCurrentPlayerVehicle

    @property
    def currentVehicleID(self):
        return self.__vehStateCtrl.getControllingVehicleID()

    @property
    def playerVehicleID(self):
        return self.__playerVehicleID

    def getControllerID(self):
        return BATTLE_CTRL_ID.VEHICLE_PASSENGER_CTRL

    def setPlayerVehicle(self, vehicleID):
        self.__playerVehicleID = vehicleID
        self.__updateVehiclePassengerInfo()

    def startControl(self, *args):
        self.__playerVehicleID = avatar_getter.getPlayerVehicleID()
        self.__updateCurrentVehicleInfo(self._getCurrentVehicle())
        self.__vehStateCtrl.onVehicleControlling += self.__updateVehiclePassengerInfo
        self.__vehStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated

    def stopControl(self):
        self.__eManager.clear()
        self.__isCurrentVehicleFPV = False
        self.__isCurrentVehicleAlive = False
        self.__playerVehicleID = UNKNOWN_VEHICLE_ID
        self.__vehStateCtrl = None
        return

    def _getCurrentVehicle(self):
        return self.__vehStateCtrl.getControllingVehicle()

    def __onVehicleStateUpdated(self, stateID, _):
        if stateID in (VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED):
            self.__updateVehiclePassengerInfo()

    def __latePassengerUpdate(self, handler):
        if self.__playerVehicleID != UNKNOWN_VEHICLE_ID:
            handler(self._getCurrentVehicle())

    def __updateCurrentVehicleInfo(self, vehicle):
        self.__isCurrentVehicleAlive = bool(vehicle is not None and vehicle.isAlive())
        self.__isCurrentVehicleFPV = avatar_getter.getIsObserverFPV()
        return

    def __updateVehiclePassengerInfo(self, vehicle=None):
        vehicle = vehicle or self._getCurrentVehicle()
        self.__updateCurrentVehicleInfo(vehicle)
        self.onVehiclePassengerUpdating(vehicle)
        self.onVehiclePassengerUpdate(vehicle)
