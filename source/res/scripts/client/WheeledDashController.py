# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/WheeledDashController.py
from __future__ import absolute_import, division
import typing
import weakref
from collections import namedtuple
import BigWorld
import CGF
from constants import PHASED_MECHANIC_STATE as MECHANIC_STATE
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.mechanics.common import IMechanicComponent
from vehicles.mechanics.generic_mechanics.wheeled_dash import createWheeledDashMiscEvents
from vehicles.mechanics.mechanic_commands import createMechanicCommandsEvents, IMechanicCommandsComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanicCommand, VehicleMechanic
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
from vehicles.mechanics.mechanic_states import IMechanicState, IMechanicStatesComponent, createMechanicStatesEvents
from vehicles.components.component_wrappers import ifPlayerVehicle
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from Input import InputAction, TriggerEvent, InputSingleton, InputTriggerPressed
from CommandMapping import CMD_CM_VEHICLE_SWITCH_AUTOROTATION
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_commands import IMechanicCommandsEvents
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents
    from vehicles.mechanics.generic_mechanics.wheeled_dash import IWheeledDashEvents

class PlayerVehicleInputPredicate(object):

    def __init__(self, entity):
        super(PlayerVehicleInputPredicate, self).__init__()
        self._entityRef = weakref.ref(entity)

    def __call__(self):
        vehicle = self._entityRef()
        return vehicle is not None and vehicle.isPlayerVehicle and vehicle.isAlive()


class WheeledDashState(namedtuple('WheeledDashState', ('state', 'baseTime', 'endTime', 'isReducedCooldown')), IMechanicState):

    @classmethod
    def fromPublicStatus(cls, publicStatus, params):
        deployTime = params.deployTime if publicStatus == MECHANIC_STATE.NOT_RUNNING else 0
        return cls(publicStatus, deployTime, 0, False)

    @classmethod
    def fromComponentStatus(cls, status):
        return cls(status.state, status.baseTime, status.endTime, status.isReducedCooldown)

    @property
    def progress(self):
        return 1.0 - self.timeLeft / self.baseTime if self.baseTime > 0 else 1.0

    @property
    def timeLeft(self):
        return max(0.0, self.endTime - BigWorld.serverTime() if self.endTime >= 0 else self.baseTime)

    def isTransition(self, other):
        return self.state != other.state


class WheeledDashController(VehicleDynamicComponent, IMechanicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):
    ACTION_NAME = 'WHEELED_DASH_ACTION'
    DEFAULT_MODE_STATE = WheeledDashState(MECHANIC_STATE.NOT_RUNNING, 0.0, -1.0, False)

    def __init__(self):
        super(WheeledDashController, self).__init__()
        self.__commandsEvents = createMechanicCommandsEvents(self)
        self.__statesEvents = createMechanicStatesEvents(self)
        self.__impulseEvents = createWheeledDashMiscEvents()
        self.__prefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__action = None
        self.__params = None
        self._initComponent()
        return

    def _onAvatarReady(self, player=None):
        self.__attachInput()
        super(WheeledDashController, self)._onAvatarReady(player)

    @ifPlayerVehicle
    def __attachInput(self, _):
        if self.__action is not None:
            return
        else:
            self.__action = action = InputAction(CMD_CM_VEHICLE_SWITCH_AUTOROTATION, [InputTriggerPressed()], PlayerVehicleInputPredicate(self.entity))
            action.bindEventReaction(TriggerEvent.Triggered, self.tryActivate)
            inputSingleton = CGF.findSingleton(self.entity.spaceID, InputSingleton)
            if inputSingleton is not None:
                inputSingleton.addAction(self.ACTION_NAME, action)
            return

    @ifPlayerVehicle
    def __detachInput(self, _):
        inputSingleton = CGF.findSingleton(self.entity.spaceID, InputSingleton)
        if inputSingleton is not None:
            inputSingleton.removeAction(self.ACTION_NAME)
        self.__action = None
        return

    @property
    def commandsEvents(self):
        return self.__commandsEvents

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.WHEELED_DASH

    @property
    def statesEvents(self):
        return self.__statesEvents

    @property
    def impulseEvents(self):
        return self.__impulseEvents

    def getMechanicState(self):
        return WheeledDashState.fromComponentStatus(self.status) if self.status else WheeledDashState.fromPublicStatus(self.publicStatus, self.__params)

    def set_status(self, _):
        self._updateComponentAppearance()

    def set_publicStatus(self, _):
        if not self.status:
            self._updateComponentAppearance()

    def onImpulseStarted(self, direction):
        self.__impulseEvents.onImpulseStarted(direction)

    def onDestroy(self):
        self.__commandsEvents.destroy()
        self.__statesEvents.destroy()
        self.__impulseEvents.destroy()
        self.__detachInput()
        super(WheeledDashController, self).onDestroy()

    def tryActivate(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.ACTIVATE)
        if self.getMechanicState().state == MECHANIC_STATE.READY:
            self.cell.tryActivate()

    def _onAppearanceReady(self):
        super(WheeledDashController, self)._onAppearanceReady()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self):
        state = self.getMechanicState()
        self.__statesEvents.updateMechanicState(state)

    def _collectComponentParams(self, typeDescriptor):
        super(WheeledDashController, self)._collectComponentParams(typeDescriptor)
        self.__params = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)
