# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/StagedJetBoostersController.py
import logging
import typing
import BigWorld
import CGF
from CommandMapping import CMD_CM_SPECIAL_ABILITY, CMD_CM_VEHICLE_SWITCH_AUTOROTATION
from cgf_components_common.vehicle_mechanics.staged_jet_boosters import StagedJetBoostersControllerDescriptor
from cgf_script.component_meta_class import registerReplicableComponent
from constants import PHASED_MECHANIC_STATE, IS_CLIENT, AcceleratorStatus
from gui.shared.utils.decorators import ReprInjector
from items.components.shared_components import StagedJetBoostersParams
from shared_utils import skipInEditor
from vehicles.components.component_wrappers import ifPlayerVehicle
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.mechanics.common import IMechanicComponent
from vehicles.mechanics.mechanic_commands import createMechanicCommandsEvents, IMechanicCommandsEvents, IMechanicCommandsComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
from vehicles.mechanics.mechanic_logging import createMechanicInputLogger, IMechanicInputLoggingComponent
from vehicles.mechanics.mechanic_states import IMechanicStatesComponent, createMechanicStatesEvents, IMechanicStatesEvents, IMechanicState
from wotdecorators import noexcept
if IS_CLIENT:
    from Input import InputAction, InputSingleton, InputTriggerPressed, TriggerEvent
_logger = logging.getLogger(__name__)

@ReprInjector.simple('state', 'endTime', 'duration', 'count', 'acceleratorStatus', 'params')
class StagedJetBoostersState(typing.NamedTuple('StagedJetBoostersState', (('state', PHASED_MECHANIC_STATE),
 ('endTime', float),
 ('duration', float),
 ('count', int),
 ('acceleratorStatus', AcceleratorStatus),
 ('params', typing.Optional[StagedJetBoostersParams]))), IMechanicState):

    @classmethod
    def fromComponentStatus(cls, status, acceleratorStatus, params):
        return cls(status.status, status.endTime, status.timeLeft, status.reuseCount, acceleratorStatus, params)

    @property
    def progress(self):
        progress = 1.0 if self.state == PHASED_MECHANIC_STATE.READY else 0.0
        if self.duration:
            timeLeft = self.timeLeft
            if self.state == PHASED_MECHANIC_STATE.ACTIVE:
                progress = timeLeft / self.duration
            else:
                progress = 1.0 - timeLeft / self.duration
        return progress

    @property
    def timeLeft(self):
        return max(0.0, self.endTime - BigWorld.serverTime())

    def isTransition(self, other):
        return self.state != other.state


@registerReplicableComponent
class StagedJetBoostersController(VehicleDynamicComponent, StagedJetBoostersControllerDescriptor, IMechanicComponent, IMechanicCommandsComponent, IMechanicStatesComponent, IMechanicInputLoggingComponent):
    _IA_NAME = 'staged_jet_boosters_input'

    @skipInEditor
    def __init__(self):
        super(StagedJetBoostersController, self).__init__()
        _logger.debug('StagedJetBoostersController.__init__()')
        self.__params = None
        self.__currentState = StagedJetBoostersState(PHASED_MECHANIC_STATE.NOT_RUNNING, 0.0, 0.0, 0, AcceleratorStatus.NONE, None)
        self.__commandsEvents = createMechanicCommandsEvents(self)
        self.__statesEvents = createMechanicStatesEvents(self)
        self.__mechanicInputLogger = createMechanicInputLogger(self, CMD_CM_SPECIAL_ABILITY, CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        self.__inputAction = None
        self._initComponent()
        return

    def onDestroy(self):
        self.detachInput()
        self.__commandsEvents.destroy()
        self.__statesEvents.destroy()
        super(StagedJetBoostersController, self).onDestroy()

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.STAGED_JET_BOOSTERS

    @property
    def commandsEvents(self):
        return self.__commandsEvents

    @property
    def statesEvents(self):
        return self.__statesEvents

    @ifPlayerVehicle
    def attachInput(self, _):
        if self.__inputAction is not None:
            return
        else:
            self.__inputAction = InputAction(CMD_CM_SPECIAL_ABILITY, [InputTriggerPressed()])
            self.__inputAction.bindEventReaction(TriggerEvent.Triggered, self.tryActivate)
            inputSingleton = CGF.findSingleton(self.entity.spaceID, InputSingleton)
            if inputSingleton is not None:
                inputSingleton.addAction(self._IA_NAME, self.__inputAction)
            return

    @ifPlayerVehicle
    def detachInput(self, _=None):
        if self.__inputAction is None:
            return
        else:
            inputSingleton = CGF.findSingleton(self.entity.spaceID, InputSingleton)
            if inputSingleton is not None:
                inputSingleton.removeAction(self._IA_NAME)
            self.__inputAction = None
            return

    def getMechanicLogState(self):
        return {'state': self.__currentState.state,
         'time_left': self.__currentState.timeLeft,
         'duration': self.__currentState.duration,
         'mechanic_name': self.vehicleMechanic.name}

    def getMechanicState(self):
        return self.__currentState

    def tryActivate(self):
        if self.stateStatus.status == PHASED_MECHANIC_STATE.READY:
            self.cell.tryActivate()
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.ACTIVATE)

    @noexcept
    def set_stateStatus(self, _=None):
        self._updateComponentAppearance()

    @noexcept
    def set_acceleratorStatus(self, prev=None):
        self._updateComponentAppearance()

    def _onAppearanceReady(self):
        super(StagedJetBoostersController, self)._onAppearanceReady()
        self.__statesEvents.processStatePrepared()

    def _onAvatarReady(self, player):
        super(StagedJetBoostersController, self)._onAvatarReady(player)
        self.__mechanicInputLogger.start()

    def _collectComponentParams(self, typeDescriptor):
        super(StagedJetBoostersController, self)._collectComponentParams(typeDescriptor)
        self.__params = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(StagedJetBoostersController, self)._onComponentAppearanceUpdate(**kwargs)
        if self.stateStatus:
            self.__currentState = StagedJetBoostersState.fromComponentStatus(self.stateStatus, self.acceleratorStatus, self.__params)
        self.__statesEvents.updateMechanicState(self.__currentState)
