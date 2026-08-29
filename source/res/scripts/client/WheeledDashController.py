# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/WheeledDashController.py
from __future__ import absolute_import, division
import typing
from collections import namedtuple
import BigWorld
from constants import PHASED_MECHANIC_STATE as MECHANIC_STATE
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.mechanics.common import IMechanicComponent
from vehicles.mechanics.generic_mechanics.wheeled_dash import createWheeledDashMiscEvents
from vehicles.mechanics.mechanic_commands import createMechanicCommandsEvents, IMechanicCommandsComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanicCommand, VehicleMechanic
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
from vehicles.mechanics.mechanic_inputs import createMechanicSingleInput
from vehicles.mechanics.mechanic_states import IMechanicState, IMechanicStatesComponent, createMechanicStatesEvents
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_commands import IMechanicCommandsEvents
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents
    from vehicles.mechanics.generic_mechanics.wheeled_dash import IWheeledDashEvents

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
    _INPUT_ACTION_NAME = 'ABILITY_1_INPUT_ACTION'
    _INPUT_PROFILE_NAME = 'ABILITY_1_INPUT_PROFILE'
    DEFAULT_MODE_STATE = WheeledDashState(MECHANIC_STATE.NOT_RUNNING, 0.0, -1.0, False)

    def __init__(self):
        super(WheeledDashController, self).__init__()
        self.__commandsEvents = createMechanicCommandsEvents(self)
        self.__statesEvents = createMechanicStatesEvents(self)
        self.__impulseEvents = createWheeledDashMiscEvents()
        self.__prefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__params = None
        self.__singleInput = None
        self._initComponent()
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
        self.__singleInput = None
        super(WheeledDashController, self).onDestroy()
        return

    def tryActivate(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.ACTIVATE)
        if self.getMechanicState().state == MECHANIC_STATE.READY:
            self.cell.tryActivate()

    def _onAvatarReady(self, player):
        super(WheeledDashController, self)._onAvatarReady(player)
        if self.__singleInput is None:
            self.__singleInput = createMechanicSingleInput(self, profileName=self._INPUT_PROFILE_NAME, actionName=self._INPUT_ACTION_NAME, inputCallback=self.tryActivate)
        return

    def _onAppearanceReady(self):
        super(WheeledDashController, self)._onAppearanceReady()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        state = self.getMechanicState()
        self.__statesEvents.updateMechanicState(state)

    def _collectComponentParams(self, typeDescriptor):
        super(WheeledDashController, self)._collectComponentParams(typeDescriptor)
        self.__params = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)
