# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PillboxSiegeComponent.py
from __future__ import absolute_import, division
import weakref
from collections import namedtuple
import BigWorld
import Input
import logging
from constants import VEHICLE_SIEGE_STATE
from gui.shared.utils.decorators import ReprInjector
from vehicles.components.component_wrappers import ifPlayerVehicle, ifObservedVehicle
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.mechanics.common import IMechanicComponent
from vehicles.mechanics.mechanic_commands import createMechanicCommandsEvents, IMechanicCommandsEvents, IMechanicCommandsComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicStatesComponent, createMechanicStatesEvents, IMechanicStatesEvents, IMechanicState
from Input import TriggerEvent
_logger = logging.getLogger(__name__)

class PlayerVehicleInputPredicate(object):

    def __init__(self, entity):
        super(PlayerVehicleInputPredicate, self).__init__()
        self._entityRef = weakref.ref(entity)

    def __call__(self):
        vehicle = self._entityRef()
        return vehicle is not None and vehicle.isPlayerVehicle and vehicle.isAlive()


class PillboxSiegeModeState(namedtuple('PillboxSiegeModeState', ('state', 'nextState', 'baseTime', 'endTime')), IMechanicState):

    @property
    def progress(self):
        return 1.0 - self.timeLeft / self.baseTime if self.baseTime > 0 else 1.0

    @property
    def timeLeft(self):
        return max(0.0, self.endTime - BigWorld.serverTime() if self.endTime >= 0 else self.baseTime)

    @property
    def isStateSwitching(self):
        return self.state != self.nextState

    def isTransition(self, other):
        return self.state != other.state or self.nextState != other.nextState

    def toSiegeState(self):
        currentMode = self.state
        nextMode = self.nextState
        if currentMode > nextMode:
            return VEHICLE_SIEGE_STATE.SWITCHING_OFF
        return VEHICLE_SIEGE_STATE.SWITCHING_ON if currentMode < nextMode else currentMode


@ReprInjector.withParent()
class PillboxSiegeComponent(VehicleDynamicComponent, IMechanicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):
    TAP_TIME = 0.25
    HOLD_TIME = 1.0
    DURATION = HOLD_TIME - TAP_TIME
    TAP_ACTION_NAME = 'pbs_tap'
    HOLD_ACTION_NAME = 'pbs_hold'
    PBS_PROFILE_NAME = 'PBS_INPUT_PROFILE'

    def __init__(self):
        super(PillboxSiegeComponent, self).__init__()
        self.__holdTime = None
        self.__mechanicPrefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__commandsEvents = createMechanicCommandsEvents(self)
        self.__statesEvents = createMechanicStatesEvents(self)
        self._initComponent()
        return

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.PILLBOX_SIEGE_MODE

    @property
    def commandsEvents(self):
        return self.__commandsEvents

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getMechanicState(self):
        baseTime = -1.0
        endTime = 0.0
        if self.status:
            baseTime = self.status.baseTime
            endTime = self.status.endTime
        src = self.publicStatus.state
        dst = self.publicStatus.nextState
        return PillboxSiegeModeState(src, dst, baseTime, endTime)

    def set_status(self, _):
        player = BigWorld.player()
        if not self.isPlayerVehicle(player):
            self._updateComponentAppearance()

    def set_publicStatus(self, _):
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__commandsEvents.destroy()
        self.__statesEvents.destroy()
        self.__detachInput()
        super(PillboxSiegeComponent, self).onDestroy()

    def _onAppearanceReady(self):
        super(PillboxSiegeComponent, self)._onAppearanceReady()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(PillboxSiegeComponent, self)._onComponentAppearanceUpdate(**kwargs)
        mechanicState = self.getMechanicState()
        self.__statesEvents.updateMechanicState(mechanicState)
        self.__notifyStateChange(mechanicState=mechanicState)

    def _onAvatarReady(self, player):
        super(PillboxSiegeComponent, self)._onAvatarReady(player)
        self.__attachInput()

    @ifPlayerVehicle
    def __attachInput(self, *_, **__):
        if not Input.inputSystem().hasProfile(self.PBS_PROFILE_NAME):
            _logger.error('[INPUT] InputProfile %s is not loaded', self.PBS_PROFILE_NAME)
            return
        tapAction = Input.inputSystem().findAction(self.PBS_PROFILE_NAME, self.TAP_ACTION_NAME)
        if tapAction:
            tapAction.setPredicate(PlayerVehicleInputPredicate(self.entity))
            tapAction.bindEventReaction(TriggerEvent.Triggered, self.__onTapCompleted)
            tapAction.bindEventReaction(TriggerEvent.Canceled, self.__onTapCanceled)
        else:
            _logger.error("[INPUT] Can't find InputAction %s/%s", self.PBS_PROFILE_NAME, self.TAP_ACTION_NAME)
        holdAction = Input.inputSystem().findAction(self.PBS_PROFILE_NAME, self.HOLD_ACTION_NAME)
        if holdAction:
            holdAction.setPredicate(PlayerVehicleInputPredicate(self.entity))
            holdAction.bindEventReaction(TriggerEvent.Started, self.__onHoldStarted)
            holdAction.bindEventReaction(TriggerEvent.Canceled, self.__onHoldCanceled)
            holdAction.bindEventReaction(TriggerEvent.Completed, self.__onHoldCompleted)
        else:
            _logger.error("[INPUT] Can't find InputAction %s/%s", self.PBS_PROFILE_NAME, self.HOLD_ACTION_NAME)
        Input.inputSystem().activateProfile(self.PBS_PROFILE_NAME)

    @ifPlayerVehicle
    def __detachInput(self, *_, **__):
        if Input.inputSystem().hasProfile(self.PBS_PROFILE_NAME):
            Input.inputSystem().deactivateProfile(self.PBS_PROFILE_NAME, unbindAllReactions=True)

    def __onTapCanceled(self):
        if self.__holdTime is not None:
            self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.PREPARING)
        return

    def __onTapCompleted(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.ACTIVATE)
        self.cell.handleShortKeyEvent()

    def __onHoldStarted(self):
        if self.entity.siegeState not in VEHICLE_SIEGE_STATE.SWITCHING:
            self.__holdTime = BigWorld.time()

    def __onHoldCompleted(self):
        if self.__holdTime is None:
            return
        else:
            self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.ALTERNATIVE_ACTIVATE)
            self.cell.handleLongKeyEvent()
            self.__holdTime = None
            return

    def __onHoldCanceled(self):
        if self.__holdTime and BigWorld.time() - self.__holdTime >= self.TAP_TIME:
            self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.CANCELLED)
        self.__holdTime = None
        return

    @ifObservedVehicle
    def __notifyStateChange(self, player, _, mechanicState):
        if player.isObserver() and not player.isObserverFPV:
            return
        player.updateSiegeStateStatus(self.entity.id, mechanicState.toSiegeState(), mechanicState.timeLeft)
