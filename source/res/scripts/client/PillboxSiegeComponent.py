# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PillboxSiegeComponent.py
import weakref
from collections import namedtuple
import BigWorld
import CGF
from constants import VEHICLE_SIEGE_STATE
from vehicles.components.component_wrappers import ifPlayerVehicle, ifObservedVehicle
from vehicles.mechanics.mechanic_commands import createMechanicCommandsEvents, IMechanicCommandsEvents, IMechanicCommandsComponent
from vehicles.components.vehicle_component import VehicleMechanicPrefabDynamicComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicStatesComponent, createMechanicStatesEvents, IMechanicStatesEvents, IMechanicState
from Input import InputAction, InputTriggerHold, TriggerEvent, InputSingleton, InputTriggerTap
from CommandMapping import CMD_CM_VEHICLE_SWITCH_AUTOROTATION

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


class PillboxSiegeComponent(VehicleMechanicPrefabDynamicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):
    TAP_TIME = 0.25
    HOLD_TIME = 1.0
    DURATION = HOLD_TIME - TAP_TIME
    TAP_ACTION_NAME = 'pbs_tap'
    HOLD_ACTION_NAME = 'pbs_hold'

    def __init__(self):
        super(PillboxSiegeComponent, self).__init__()
        self.__tapAction = None
        self.__holdAction = None
        self.__holdTime = None
        self.__commandsEvents = createMechanicCommandsEvents()
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
        baseTime = -1.0
        endTime = 0.0
        if self.status:
            baseTime = self.status.baseTime
            endTime = self.status.endTime
        src = self.publicStatus.state
        dst = self.publicStatus.nextState
        return PillboxSiegeModeState(src, dst, baseTime, endTime)

    def set_publicStatus(self, _):
        self._updateComponentAppearance()

    def set_status(self, _):
        player = BigWorld.player()
        if not self.isPlayerVehicle(player):
            self._updateComponentAppearance()

    def onDestroy(self):
        self.__commandsEvents.destroy()
        self.__statesEvents.destroy()
        self.__detachInput()
        super(PillboxSiegeComponent, self).onDestroy()

    def _onAppearanceReady(self):
        self.__statesEvents.processStatePrepared()
        super(PillboxSiegeComponent, self)._onAppearanceReady()

    def _onComponentAppearanceUpdate(self):
        mechanicState = self.getMechanicState()
        self.__statesEvents.updateMechanicState(mechanicState)
        self.__notifyStateChange(mechanicState=mechanicState)

    def _onAvatarReady(self, player=None):
        self.__attachInput()
        super(PillboxSiegeComponent, self)._onComponentAvatarUpdate(player)

    @ifPlayerVehicle
    def __attachInput(self, _):
        if self.__tapAction is not None or self.__holdAction is not None:
            return
        else:
            self.__tapAction = tapAction = InputAction(CMD_CM_VEHICLE_SWITCH_AUTOROTATION, [InputTriggerTap(self.TAP_TIME)], PlayerVehicleInputPredicate(self.entity))
            tapAction.bindEventReaction(TriggerEvent.Triggered, self.__onTapCompleted)
            tapAction.bindEventReaction(TriggerEvent.Canceled, self.__onTapCanceled)
            self.__holdAction = holdAction = InputAction(CMD_CM_VEHICLE_SWITCH_AUTOROTATION, [InputTriggerHold(self.HOLD_TIME)], PlayerVehicleInputPredicate(self.entity))
            holdAction.bindEventReaction(TriggerEvent.Started, self.__onHoldStarted)
            holdAction.bindEventReaction(TriggerEvent.Canceled, self.__onHoldCanceled)
            holdAction.bindEventReaction(TriggerEvent.Completed, self.__onHoldCompleted)
            inputSingleton = CGF.findSingleton(self.entity.spaceID, InputSingleton)
            if inputSingleton is not None:
                inputSingleton.addAction(self.TAP_ACTION_NAME, tapAction)
                inputSingleton.addAction(self.HOLD_ACTION_NAME, holdAction)
            return

    @ifPlayerVehicle
    def __detachInput(self, _):
        inputSingleton = CGF.findSingleton(self.entity.spaceID, InputSingleton)
        if inputSingleton is not None:
            inputSingleton.removeAction(self.TAP_ACTION_NAME)
            inputSingleton.removeAction(self.HOLD_ACTION_NAME)
        self.__tapAction = None
        self.__holdAction = None
        return

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
