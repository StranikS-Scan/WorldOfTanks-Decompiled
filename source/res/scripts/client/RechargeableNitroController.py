# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/RechargeableNitroController.py
import logging
import typing
import BigWorld
from constants import RECHARGEABLE_NITRO_STATE
from items.components.shared_components import RechargeableNitroParams
from vehicles.components.vehicle_component import VehicleMechanicPrefabDynamicComponent
from vehicles.mechanics.mechanic_commands import createMechanicCommandsEvents
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_commands import IMechanicCommandsComponent
from vehicles.mechanics.mechanic_states import IMechanicState, IMechanicStatesComponent, createMechanicStatesEvents
from vehicles.mechanics.mechanic_helpers import getVehicleMechanicParams
if typing.TYPE_CHECKING:
    from typing import Any, Optional
    from vehicles.mechanics.mechanic_commands import IMechanicCommandsEvents
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents
_logger = logging.getLogger(__name__)

class RechargeableNitroState(typing.NamedTuple('RechargeableNitroState', (('state', RECHARGEABLE_NITRO_STATE),
 ('endTime', float),
 ('remainingTime', float),
 ('isCharged', bool),
 ('isEmpty', bool),
 ('isBelowThreshold', bool),
 ('params', typing.Optional[RechargeableNitroParams]))), IMechanicState):

    @classmethod
    def fromComponentStatus(cls, status, params):
        return cls(status.status, status.endTime, status.remainingTime, bool(status.isCharged), bool(status.isEmpty), status.isBelowThreshold, params)

    @property
    def progress(self):
        progress = 1.0
        if not self.params:
            return progress
        if self.timeLeft:
            if self.state in [RECHARGEABLE_NITRO_STATE.DEPLETING, RECHARGEABLE_NITRO_STATE.ACTIVE]:
                progress = min(1.0, self.timeLeft / self.params.duration)
            elif self.state == RECHARGEABLE_NITRO_STATE.PREPARING:
                reloadFactor = self.params.reloadTime / self.params.duration
                remainingReload = (self.params.duration - self.remainingTime) * reloadFactor
                cooldownCalc = (self.params.duration * self.params.threshold - self.remainingTime) * reloadFactor
                cooldown = max(self.params.cooldown, cooldownCalc)
                reloadDiff = remainingReload - (cooldown - self.timeLeft)
                progress = max(0.0, 1.0 - reloadDiff / self.params.reloadTime)
            elif self.state in [RECHARGEABLE_NITRO_STATE.DEPLOYING, RECHARGEABLE_NITRO_STATE.READY]:
                progress = 1.0
            else:
                progress = max(0.0, 1.0 - self.timeLeft / self.params.reloadTime)
        return progress

    @property
    def timeLeft(self):
        return max(0.0, self.endTime - BigWorld.serverTime())

    def isTransition(self, other):
        return self.state != other.state


class RechargeableNitroController(VehicleMechanicPrefabDynamicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):

    def __init__(self):
        super(RechargeableNitroController, self).__init__()
        self.__commandsEvents = createMechanicCommandsEvents()
        self.__params = None
        self.__currentState = RechargeableNitroState(RECHARGEABLE_NITRO_STATE.NOT_RUNNING, 0.0, 0.0, False, False, False, None)
        self.__statesEvents = createMechanicStatesEvents(self)
        self._initComponent()
        return

    @property
    def commandsEvents(self):
        return self.__commandsEvents

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getMechanicState(self):
        return self.__currentState

    def set_stateStatus(self, _):
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__commandsEvents.destroy()
        self.__statesEvents.destroy()
        super(RechargeableNitroController, self).onDestroy()

    def tryActivate(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.ACTIVATE)
        if self.__currentState.state in RECHARGEABLE_NITRO_STATE.READY_STATES:
            self.cell.tryActivate()

    def tryDeactivate(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.DEACTIVATE)
        if self.__currentState.state in RECHARGEABLE_NITRO_STATE.ACTIVE_STATES:
            self.cell.tryDeactivate()

    def alternateOnState(self):
        if self.__currentState.state in RECHARGEABLE_NITRO_STATE.ACTIVE_STATES:
            self.tryDeactivate()
        else:
            self.tryActivate()

    def _onAppearanceReady(self):
        super(RechargeableNitroController, self)._onAppearanceReady()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self):
        if self.stateStatus:
            self.__currentState = RechargeableNitroState.fromComponentStatus(self.stateStatus, self.__params)
        self.__statesEvents.updateMechanicState(self.__currentState)

    def _collectComponentParams(self, typeDescriptor):
        super(RechargeableNitroController, self)._collectComponentParams(typeDescriptor)
        self.__params = getVehicleMechanicParams(VehicleMechanic.RECHARGEABLE_NITRO, typeDescriptor)
