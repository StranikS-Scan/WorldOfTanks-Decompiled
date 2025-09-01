# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/StationaryReloadController.py
import typing
from collections import namedtuple
import BigWorld
from constants import STATIONARY_RELOAD_STATE, GUN_LOCK_REASONS
from vehicles.mechanics.mechanic_commands import IMechanicCommandsComponent, createMechanicCommandsEvents
from vehicles.components.vehicle_component import VehicleMechanicPrefabDynamicComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_helpers import getVehicleMechanic
from vehicles.mechanics.mechanic_states import IMechanicStatesEvents, createMechanicStatesEvents, IMechanicStatesComponent, IMechanicState
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle
    from typing import Optional, Any
    from vehicles.mechanics.mechanic_commands import IMechanicCommandsEvents

def getVehicleStationaryReloadController(vehicle):
    return getVehicleMechanic(VehicleMechanic.STATIONARY_RELOAD, vehicle)


class StationaryReloadState(namedtuple('StationaryReloadState', ('state', 'baseTime', 'timeLeft', 'gunLockMask', 'sequenceEndTime')), IMechanicState):

    @classmethod
    def fromComponentStatus(cls, status):
        return cls(status.state, status.baseTime, status.timeLeft, status.gunLockMask, status.sequenceEndTime)

    def isTransition(self, other):
        return self.state != other.state or self.gunLockMask != other.gunLockMask

    @property
    def isShootPossible(self):
        return self.state == STATIONARY_RELOAD_STATE.IDLE

    @property
    def isReloadingBlocked(self):
        return self.state not in (STATIONARY_RELOAD_STATE.RELOADING, STATIONARY_RELOAD_STATE.IDLE)

    @property
    def sequenceTimeLeft(self):
        return max(0, self.sequenceEndTime - BigWorld.serverTime())


class StationaryReloadController(VehicleMechanicPrefabDynamicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):
    DEFAULT_MODE_STATE = StationaryReloadState(STATIONARY_RELOAD_STATE.IDLE, 0.0, 0.0, GUN_LOCK_REASONS.NONE, 0.0)

    def __init__(self):
        super(StationaryReloadController, self).__init__()
        self.__commandsEvents = createMechanicCommandsEvents()
        self.__statesEvents = createMechanicStatesEvents(self)
        self._initComponent()

    def set_status(self, _):
        self._updateComponentAppearance()

    @property
    def commandsEvents(self):
        return self.__commandsEvents

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getMechanicState(self):
        return StationaryReloadState.fromComponentStatus(self.status if self.status else self.DEFAULT_MODE_STATE)

    def onDestroy(self):
        self.__commandsEvents.destroy()
        self.__statesEvents.destroy()
        super(StationaryReloadController, self).onDestroy()

    def tryActivate(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.MANUAL_RELOAD)
        return False

    def _onAppearanceReady(self):
        self.__statesEvents.processStatePrepared()
        super(StationaryReloadController, self)._onAppearanceReady()

    def _onComponentAppearanceUpdate(self):
        self.__statesEvents.updateMechanicState(self.getMechanicState())
        BigWorld.player().updateStationaryReloadingState(self.getMechanicState())
