# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/vehicle_mechanics_blocks.py
import BigWorld
import typing
from constants import OVERHEAT_GAIN_STATE, TARGET_DESIGNATOR_STATE
from events_handler import eventHandler
from vehicles.mechanics.mechanic_commands import IMechanicCommandsListenerLogic
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VEHICLE_MECHANIC_USED_COMMANDS
from visual_script.block import Block
from visual_script.misc import ASPECT
from visual_script.slot_types import SLOT_TYPE
from visual_script.vehicle_mechanics_blocks import ConcentrationModeStateEnum, PowerModeStateEnum, SecondaryGunStateEnum, VehicleSiegeStateEnum, OverheatGainStateEnum, RechargeableNitroStateEnum, TargetDesignatorStateEnum, StationaryReloadEnum, StationaryReloadLockEnum
from visual_script_client.vehicle_mechanics_common import VehicleSelectableMechanicEventsBlock, VehicleMechanicStateEventsBlock, VehicleMechanicLifeCycleEventsBlock
if typing.TYPE_CHECKING:
    from typing import Any, List
    from _weakref import ReferenceType
    from AccuracyStacksController import AccuracyStacksState
    from BattleFuryController import BattleFuryState
    from ConcentrationModeComponent import ConcentrationModeState
    from SupportWeaponComponent import SupportWeaponState
    from PillboxSiegeComponent import PillboxSiegeModeState
    from vehicles.mechanics.mechanic_constants import VehicleMechanicCommand
    from PowerModeController import PowerModeState
    from OverheatStacksController import OverheatStacksState
    from StanceDanceController import StanceDanceState
    from RechargeableNitroController import RechargeableNitroState
    from ChargeShotComponent import ChargeShotState, ChargeShotComponent
    from TargetDesignatorController import TargetDesignatorState
    from StationaryReloadController import StationaryReloadState

class OnVehicleMechanicCommand(VehicleSelectableMechanicEventsBlock, IMechanicCommandsListenerLogic):
    _EVENTS_NAME = 'commands'

    def __init__(self, *args, **kwargs):
        super(OnVehicleMechanicCommand, self).__init__(*args, **kwargs)
        self._commands = {command:self._makeEventOutputSlot(command.value) for command in VEHICLE_MECHANIC_USED_COMMANDS[self._vehicleMechanic]}

    @eventHandler
    def onMechanicCommand(self, command):
        self._commands[command].call()

    @classmethod
    def _getInitParamMechanics(cls):
        return sorted((mechanic.value for mechanic in VEHICLE_MECHANIC_USED_COMMANDS))

    def _subscribeToMechanicComponent(self, mechanicComponent):
        super(OnVehicleMechanicCommand, self)._subscribeToMechanicComponent(mechanicComponent)
        self.subscribeTo(mechanicComponent.commandsEvents)

    def _unsubscribeFromMechanicComponent(self, mechanicComponent):
        self.unsubscribeFrom(mechanicComponent.commandsEvents)
        super(OnVehicleMechanicCommand, self)._unsubscribeFromMechanicComponent(mechanicComponent)


class OnConcentrationModeState(VehicleMechanicStateEventsBlock):

    def __init__(self, *args, **kwargs):
        super(OnConcentrationModeState, self).__init__(*args, **kwargs)
        self._state = self._makeDataOutputSlot('state', ConcentrationModeStateEnum.slotType(), None)
        return

    @classmethod
    def _getVehicleMechanic(cls, initParams):
        return VehicleMechanic.CONCENTRATION_MODE

    def _onStatePrepared(self, state):
        self._state.setValue(state.state)

    def _onStateObservation(self, state):
        self._state.setValue(state.state)

    def _onStateTransition(self, prevState, newState):
        self._state.setValue(newState.state)


class OnPowerModeState(VehicleMechanicStateEventsBlock):

    def __init__(self, *args, **kwargs):
        super(OnPowerModeState, self).__init__(*args, **kwargs)
        self._state = self._makeDataOutputSlot('state', PowerModeStateEnum.slotType(), None)
        return

    @classmethod
    def _getVehicleMechanic(cls, initParams):
        return VehicleMechanic.POWER_MODE

    def _onStatePrepared(self, state):
        self._state.setValue(state.state)

    def _onStateTransition(self, prevState, newState):
        self._state.setValue(newState.state)

    def _onStateObservation(self, state):
        self._state.setValue(state.state)


class OnPillboxSiegeModeState(VehicleMechanicStateEventsBlock):

    def __init__(self, *args, **kwargs):
        super(OnPillboxSiegeModeState, self).__init__(*args, **kwargs)
        self._state = self._makeDataOutputSlot('state', VehicleSiegeStateEnum.slotType(), None)
        self._nextState = self._makeDataOutputSlot('nextState', VehicleSiegeStateEnum.slotType(), None)
        return

    @classmethod
    def _getVehicleMechanic(cls, initParams):
        return VehicleMechanic.PILLBOX_SIEGE_MODE

    def _onStatePrepared(self, state):
        self._state.setValue(state.state)
        self._nextState.setValue(state.nextState)

    def _onStateObservation(self, state):
        self._state.setValue(state.state)
        self._nextState.setValue(state.nextState)

    def _onStateTransition(self, _, newState):
        self._state.setValue(newState.state)
        self._nextState.setValue(newState.nextState)


class OnRechargeableNitroState(VehicleMechanicStateEventsBlock):

    def __init__(self, *args, **kwargs):
        super(OnRechargeableNitroState, self).__init__(*args, **kwargs)
        self._state = self._makeDataOutputSlot('state', RechargeableNitroStateEnum.slotType(), None)
        self._isCharged = self._makeDataOutputSlot('isCharged', SLOT_TYPE.BOOL, None)
        self._isEmpty = self._makeDataOutputSlot('isEmpty', SLOT_TYPE.BOOL, None)
        return

    @classmethod
    def _getVehicleMechanic(cls, initParams):
        return VehicleMechanic.RECHARGEABLE_NITRO

    def __forwardStateToVSE(self, state):
        self._state.setValue(state.state)
        self._isCharged.setValue(state.isCharged)
        self._isEmpty.setValue(state.isEmpty)

    def _onStatePrepared(self, state):
        self.__forwardStateToVSE(state)

    def _onStateTransition(self, prevState, newState):
        self.__forwardStateToVSE(newState)

    def _onStateObservation(self, state):
        self.__forwardStateToVSE(state)


class OnBattleFuryState(VehicleMechanicStateEventsBlock):

    def __init__(self, *args, **kwargs):
        super(OnBattleFuryState, self).__init__(*args, **kwargs)
        self._prevLevelSlot = self._makeDataOutputSlot('prevLevel', SLOT_TYPE.INT, None)
        self._levelSlot = self._makeDataOutputSlot('level', SLOT_TYPE.INT, None)
        self._maxLevel = self._makeDataOutputSlot('maxLevel', SLOT_TYPE.INT, None)
        self._prevEndTimeSlot = self._makeDataOutputSlot('prevEndTime', SLOT_TYPE.FLOAT, None)
        self._endTimeSlot = self._makeDataOutputSlot('endTime', SLOT_TYPE.FLOAT, None)
        self._prevLevel = 0
        self._level = 0
        self._prevEndTime = 0.0
        self._endTime = 0.0
        return

    @classmethod
    def _getVehicleMechanic(cls, initParams):
        return VehicleMechanic.BATTLE_FURY

    def __recacheState(self, newState):
        self._prevLevel = self._level
        self._level = newState.level
        self._prevEndTime = self._endTime
        self._endTime = newState.endTime

    def __setSlots(self):
        self._prevLevelSlot.setValue(self._prevLevel)
        self._levelSlot.setValue(self._level)
        self._prevEndTimeSlot.setValue(self._prevEndTime)
        self._endTimeSlot.setValue(self._endTime)

    def _onStateObservation(self, state):
        self.__recacheState(state)
        self.__setSlots()

    def _onStatePrepared(self, state):
        self.__recacheState(state)
        self.__setSlots()
        self._maxLevel.setValue(state.maxLevel)

    def _onStateTransition(self, prevState, newState):
        self.__recacheState(newState)
        self.__setSlots()


class OnOverheatStacksState(VehicleMechanicStateEventsBlock):

    def __init__(self, *args, **kwargs):
        super(OnOverheatStacksState, self).__init__(*args, **kwargs)
        self._prevGainState = self._makeDataOutputSlot('prevGainState', OverheatGainStateEnum.slotType(), None)
        self._gainState = self._makeDataOutputSlot('gainState', OverheatGainStateEnum.slotType(), None)
        self._prevLevel = self._makeDataOutputSlot('prevLevel', SLOT_TYPE.INT, None)
        self._level = self._makeDataOutputSlot('level', SLOT_TYPE.INT, None)
        self._maxLevel = self._makeDataOutputSlot('maxLevel', SLOT_TYPE.INT, None)
        self._prevGainState.setValue(OVERHEAT_GAIN_STATE.NULL_STATE)
        self._gainState.setValue(OVERHEAT_GAIN_STATE.NULL_STATE)
        self._prevLevel.setValue(0)
        self._level.setValue(0)
        self._maxLevel.setValue(0)
        return

    @classmethod
    def _getVehicleMechanic(cls, initParams):
        return VehicleMechanic.OVERHEAT_STACKS

    def _onStatePrepared(self, state):
        self._gainState.setValue(state.gainState)
        self._level.setValue(state.level)
        self._maxLevel.setValue(state.maxLevel)

    def _onStateObservation(self, state):
        self._gainState.setValue(state.gainState)
        self._level.setValue(state.level)

    def _onStateTransition(self, prevState, newState):
        self._prevGainState.setValue(prevState.gainState)
        self._gainState.setValue(newState.gainState)
        self._prevLevel.setValue(prevState.level)
        self._level.setValue(newState.level)


class OnAccuracyStacksState(VehicleMechanicStateEventsBlock):

    def __init__(self, *args, **kwargs):
        super(OnAccuracyStacksState, self).__init__(*args, **kwargs)
        self._prevIsGainingActive = self._makeDataOutputSlot('prevIsGainingActive', SLOT_TYPE.BOOL, None)
        self._isGainingActive = self._makeDataOutputSlot('isGainingActive', SLOT_TYPE.BOOL, None)
        self._prevLevel = self._makeDataOutputSlot('prevLevel', SLOT_TYPE.INT, None)
        self._level = self._makeDataOutputSlot('level', SLOT_TYPE.INT, None)
        self._maxLevel = self._makeDataOutputSlot('maxLevel', SLOT_TYPE.INT, None)
        return

    @classmethod
    def _getVehicleMechanic(cls, initParams):
        return VehicleMechanic.ACCURACY_STACKS

    def _onStatePrepared(self, state):
        self._prevIsGainingActive.setValue(False)
        self._isGainingActive.setValue(state.isGainingActive)
        self._prevLevel.setValue(0)
        self._level.setValue(state.level)
        self._maxLevel.setValue(state.maxLevel)

    def _onStateObservation(self, state):
        self._prevIsGainingActive.setValue(state.isGainingActive)
        self._isGainingActive.setValue(state.isGainingActive)
        self._prevLevel.setValue(state.level)
        self._level.setValue(state.level)
        self._maxLevel.setValue(state.maxLevel)

    def _onStateTransition(self, prevState, newState):
        self._prevIsGainingActive.setValue(prevState.isGainingActive)
        self._isGainingActive.setValue(newState.isGainingActive)
        self._prevLevel.setValue(prevState.level)
        self._level.setValue(newState.level)
        self._maxLevel.setValue(newState.maxLevel)


class OnSupportWeaponState(VehicleMechanicStateEventsBlock):

    def __init__(self, *args, **kwargs):
        super(OnSupportWeaponState, self).__init__(*args, **kwargs)
        self._state = self._makeDataOutputSlot('state', SecondaryGunStateEnum.slotType(), None)
        self._timeLeft = self._makeDataOutputSlot('timeLeft', SLOT_TYPE.FLOAT, None)
        return

    @classmethod
    def _getVehicleMechanic(cls, initParams):
        return VehicleMechanic.SUPPORT_WEAPON

    def _onStatePrepared(self, state):
        self._state.setValue(state.state)
        self._timeLeft.setValue(state.timeLeft)

    def _onStateObservation(self, state):
        self._state.setValue(state.state)
        self._timeLeft.setValue(state.timeLeft)

    def _onStateTransition(self, prevState, newState):
        self._state.setValue(newState.state)
        self._timeLeft.setValue(newState.timeLeft)


class OnStanceDanceState(VehicleMechanicStateEventsBlock):

    def __init__(self, *args, **kwargs):
        super(OnStanceDanceState, self).__init__(*args, **kwargs)
        self._isFightState = self._makeDataOutputSlot('isFightState', SLOT_TYPE.BOOL, None)
        self._isTurboState = self._makeDataOutputSlot('isTurboState', SLOT_TYPE.BOOL, None)
        self._isActiveFightState = self._makeDataOutputSlot('isActiveFightState', SLOT_TYPE.BOOL, None)
        self._isActiveTurboState = self._makeDataOutputSlot('isActiveTurboState', SLOT_TYPE.BOOL, None)
        self._isEngineDeadState = self._makeDataOutputSlot('isEngineDeadState', SLOT_TYPE.BOOL, None)
        self._isSwitchingState = self._makeDataOutputSlot('isSwitchingState', SLOT_TYPE.BOOL, None)
        self._fightEnergyRatio = self._makeDataOutputSlot('fightEnergyRatio', SLOT_TYPE.FLOAT, None)
        self._turboEnergyRatio = self._makeDataOutputSlot('turboEnergyRatio', SLOT_TYPE.FLOAT, None)
        self._isEnoughEnergyToActivate = self._makeDataOutputSlot('isEnoughEnergyToActivate', SLOT_TYPE.BOOL, None)
        self._prevIsFightState = self._makeDataOutputSlot('prevIsFightState', SLOT_TYPE.BOOL, None)
        self._prevIsTurboState = self._makeDataOutputSlot('prevIsTurboState', SLOT_TYPE.BOOL, None)
        self._prevIsActiveFightState = self._makeDataOutputSlot('prevIsActiveFightState', SLOT_TYPE.BOOL, None)
        self._prevIsActiveTurboState = self._makeDataOutputSlot('prevIsActiveTurboState', SLOT_TYPE.BOOL, None)
        self._prevIsEngineDeadState = self._makeDataOutputSlot('prevIsEngineDeadState', SLOT_TYPE.BOOL, None)
        self._prevIsSwitchingState = self._makeDataOutputSlot('prevIsSwitchingState', SLOT_TYPE.BOOL, None)
        self._isFightState.setValue(False)
        self._isTurboState.setValue(False)
        self._isActiveFightState.setValue(False)
        self._isActiveTurboState.setValue(False)
        self._isEngineDeadState.setValue(False)
        self._isSwitchingState.setValue(False)
        self._fightEnergyRatio.setValue(0.0)
        self._turboEnergyRatio.setValue(0.0)
        self._isEnoughEnergyToActivate.setValue(False)
        self._prevIsFightState.setValue(False)
        self._prevIsTurboState.setValue(False)
        self._prevIsActiveFightState.setValue(False)
        self._prevIsActiveTurboState.setValue(False)
        self._prevIsEngineDeadState.setValue(False)
        self._prevIsSwitchingState.setValue(False)
        return

    @classmethod
    def _getVehicleMechanic(cls, initParams):
        return VehicleMechanic.STANCE_DANCE

    def _onStatePrepared(self, state):
        self.__updateCurrentState(state)
        self.__updatePrevState(state)

    def _onStateObservation(self, state):
        self.__updateCurrentState(state)
        self.__updatePrevState(state)

    def _onStateTransition(self, prevState, newState):
        self.__updateCurrentState(newState)
        self.__updatePrevState(prevState)

    def __updateCurrentState(self, state):
        self._isFightState.setValue(state.isFightState)
        self._isTurboState.setValue(state.isTurboState)
        self._isActiveFightState.setValue(state.isActiveFightState)
        self._isActiveTurboState.setValue(state.isActiveTurboState)
        self._isEngineDeadState.setValue(state.isEngineDeadState)
        self._isSwitchingState.setValue(state.isSwitchingState)
        self._fightEnergyRatio.setValue(state.getFightEnergyRatio)
        self._turboEnergyRatio.setValue(state.getTurboEnergyRatio)
        self._isEnoughEnergyToActivate.setValue(state.isEnoughEnergyToActivate)

    def __updatePrevState(self, state):
        self._prevIsFightState.setValue(state.isFightState)
        self._prevIsTurboState.setValue(state.isTurboState)
        self._prevIsActiveFightState.setValue(state.isActiveFightState)
        self._prevIsActiveTurboState.setValue(state.isActiveTurboState)
        self._prevIsEngineDeadState.setValue(state.isEngineDeadState)
        self._prevIsSwitchingState.setValue(state.isSwitchingState)


class OnChargeShotState(VehicleMechanicStateEventsBlock, VehicleMechanicLifeCycleEventsBlock):

    def __init__(self, *args, **kwargs):
        super(OnChargeShotState, self).__init__(*args, **kwargs)
        self._level = self._makeDataOutputSlot('level', SLOT_TYPE.INT, None)
        self._maxLevel = self._makeDataOutputSlot('maxLevel', SLOT_TYPE.INT, None)
        self._isCharging = self._makeDataOutputSlot('isCharging', SLOT_TYPE.BOOL, None)
        self._isShotBlock = self._makeDataOutputSlot('isShotBlock', SLOT_TYPE.BOOL, None)
        self._canStart = self._makeDataOutputSlot('canStart', SLOT_TYPE.BOOL, None)
        self._isGunDestroyed = self._makeDataOutputSlot('isGunDestroyed', SLOT_TYPE.BOOL, None)
        self._prevLevel = self._makeDataOutputSlot('prevLevel', SLOT_TYPE.INT, None)
        self._prevIsCharging = self._makeDataOutputSlot('prevIsCharging', SLOT_TYPE.BOOL, None)
        self._prevIsShotBlock = self._makeDataOutputSlot('prevIsShotBlock', SLOT_TYPE.BOOL, None)
        self._prevIsGunDestroyed = self._makeDataOutputSlot('prevIsGunDestroyed', SLOT_TYPE.BOOL, None)
        self._level.setValue(0)
        self._maxLevel.setValue(0)
        self._isCharging.setValue(False)
        self._isShotBlock.setValue(False)
        self._canStart.setValue(False)
        self._prevLevel.setValue(0)
        self._prevIsCharging.setValue(False)
        self._prevIsShotBlock.setValue(False)
        return

    @classmethod
    def _getVehicleMechanic(cls, initParams):
        return VehicleMechanic.CHARGE_SHOT

    def _onStatePrepared(self, state):
        self.__updateStateParams(state)

    def _onStateObservation(self, state):
        self.__updateStateParams(state)

    def _onComponentParamsCollected(self, component):
        params = component.params
        if params is not None:
            self._maxLevel.setValue(params.maxLevel)
        return

    def _onStateTransition(self, prevState, newState):
        self._prevLevel.setValue(prevState.level)
        self._prevIsCharging.setValue(prevState.hasCharging)
        self._prevIsShotBlock.setValue(prevState.hasShotBlock)
        self._prevIsGunDestroyed.setValue(prevState.isGunDestroyed)
        self.__updateStateParams(newState)

    def __updateStateParams(self, currentState):
        self._level.setValue(currentState.level)
        self._isCharging.setValue(currentState.hasCharging)
        self._isShotBlock.setValue(currentState.hasShotBlock)
        self._canStart.setValue(currentState.canStart)
        self._isGunDestroyed.setValue(currentState.isGunDestroyed)


class OnTargetDesignatorState(VehicleMechanicStateEventsBlock):

    def __init__(self, *args, **kwargs):
        super(OnTargetDesignatorState, self).__init__(*args, **kwargs)
        self._state = self._makeDataOutputSlot('state', TargetDesignatorStateEnum.slotType(), None)
        self._prevState = self._makeDataOutputSlot('prevState', TargetDesignatorStateEnum.slotType(), None)
        self._endTime = self._makeDataOutputSlot('endTime', SLOT_TYPE.FLOAT, None)
        self._state.setValue(TARGET_DESIGNATOR_STATE.COOLDOWN)
        self._prevState.setValue(TARGET_DESIGNATOR_STATE.COOLDOWN)
        self._endTime.setValue(0.0)
        return

    @classmethod
    def _getVehicleMechanic(cls, initParams):
        return VehicleMechanic.TARGET_DESIGNATOR

    def _onStatePrepared(self, state):
        self.__updateState(state)

    def _onStateObservation(self, state):
        self.__updateState(state)

    def _onStateTransition(self, prevState, newState):
        self._prevState.setValue(prevState.state)
        self.__updateState(newState)

    def __updateState(self, state):
        self._state.setValue(state.state)
        self._endTime.setValue(state.endTime)


class ServerTime(Block):

    def __init__(self, *args, **kwargs):
        super(ServerTime, self).__init__(*args, **kwargs)
        self._currentTimestamp = self._makeDataOutputSlot('currentTimestamp', SLOT_TYPE.FLOAT, self._execValue)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    def _execValue(self):
        self._currentTimestamp.setValue(BigWorld.serverTime())


class OnStationaryReloadState(VehicleMechanicStateEventsBlock):

    def __init__(self, *args, **kwargs):
        super(OnStationaryReloadState, self).__init__(*args, **kwargs)
        self._state = self._makeDataOutputSlot('state', StationaryReloadEnum.slotType(), None)
        self._lockState = self._makeDataOutputSlot('lockState', StationaryReloadLockEnum.slotType(), None)
        return

    @classmethod
    def _getVehicleMechanic(cls, initParams):
        return VehicleMechanic.STATIONARY_RELOAD

    def _onStatePrepared(self, state):
        self._state.setValue(state.state)
        self._lockState.setValue(state.gunLockMask)

    def _onStateObservation(self, state):
        self._state.setValue(state.state)
        self._lockState.setValue(state.gunLockMask)

    def _onStateTransition(self, prevState, newState):
        self._state.setValue(newState.state)
        self._lockState.setValue(newState.gunLockMask)
