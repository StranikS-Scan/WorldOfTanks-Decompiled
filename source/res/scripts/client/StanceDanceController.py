# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/StanceDanceController.py
import typing
import BigWorld
import math_utils
from constants import STANCE_DANCE_STATE
from gui.shared.utils.decorators import ReprInjector
from items.components.shared_components import StanceDanceParams
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.mechanics.common import IMechanicComponent
from vehicles.mechanics.mechanic_commands import createMechanicCommandsEvents, IMechanicCommandsComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
from vehicles.mechanics.mechanic_states import createMechanicStatesEvents, IMechanicStatesComponent, IMechanicState
if typing.TYPE_CHECKING:
    from typing import Any, Optional, Dict
    from vehicles.mechanics.mechanic_commands import IMechanicCommandsEvents
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents
_LOG_STANCE_DANCE_DEBUG = False

@ReprInjector.simple('state', 'energyTurbo', 'energyFight', 'transitionTimeLeft', 'timeLeftActiveTurbo', 'timeLeftActiveFight')
class StanceDanceState(typing.NamedTuple('StanceDanceState', (('state', int),
 ('params', StanceDanceParams),
 ('energyTurbo', int),
 ('startTimeTurbo', float),
 ('durationTurbo', float),
 ('energyFight', int),
 ('startTimeFight', float),
 ('durationFight', float),
 ('startSwitch', float),
 ('durationSwitch', float))), IMechanicState):

    @classmethod
    def fromComponentStatus(cls, status, params):
        state = cls(status.state, params, status.energyTurbo, status.timeActiveTurbo['startTime'], status.timeActiveTurbo['endTime'] - status.timeActiveTurbo['startTime'], status.energyFight, status.timeActiveFight['startTime'], status.timeActiveFight['endTime'] - status.timeActiveFight['startTime'], status.timeSwitch['startTime'], status.timeSwitch['endTime'] - status.timeSwitch['startTime'])
        return state

    @property
    def getFightEnergyRatio(self):
        return 1 - self.progressFight if self.isActiveFightState else math_utils.clamp(0.0, 1.0, self.energyFight / self.params.maxEnergy)

    @property
    def getTurboEnergyRatio(self):
        return 1 - self.progressTurbo if self.isActiveTurboState else math_utils.clamp(0.0, 1.0, self.energyTurbo / self.params.maxEnergy)

    @property
    def timeLeftActiveFight(self):
        now = BigWorld.serverTime()
        if self.isActiveFightState:
            endTime = self.startTimeFight + self.durationFight
            return max(0.0, endTime - now)

    @property
    def timeLeftActiveTurbo(self):
        now = BigWorld.serverTime()
        if self.isActiveTurboState:
            endTime = self.startTimeTurbo + self.durationTurbo
            return max(0.0, endTime - now)

    @property
    def transitionTimeLeft(self):
        if not self.isSwitchingState:
            return 0.0
        if self.isEngineDeadState:
            return self.params.timeSwitchStance - self.durationSwitch
        endTime = self.startSwitch + self.durationSwitch
        return max(0.0, endTime - BigWorld.serverTime())

    @property
    def isFightState(self):
        return self.state & STANCE_DANCE_STATE.STANCE_MASK == STANCE_DANCE_STATE.STANCE_FIGHT

    @property
    def isTurboState(self):
        return self.state & STANCE_DANCE_STATE.STANCE_MASK == STANCE_DANCE_STATE.STANCE_TURBO

    @property
    def isActiveFightState(self):
        return bool(self.state & STANCE_DANCE_STATE.ACTIVE_ABILITY_FIGHT)

    @property
    def isActiveTurboState(self):
        return bool(self.state & STANCE_DANCE_STATE.ACTIVE_ABILITY_TURBO)

    @property
    def isSwitchingState(self):
        return bool(self.state & STANCE_DANCE_STATE.SWITCHING_STANCE)

    @property
    def isEngineDeadState(self):
        return bool(self.state & STANCE_DANCE_STATE.ENGINE_DEAD)

    @property
    def isGainingEnergy(self):
        return bool(self.state & STANCE_DANCE_STATE.ENERGY_GAIN_MASK)

    @property
    def isGainingEnergyBoosted(self):
        return bool(self.state & STANCE_DANCE_STATE.ENERGY_SPD_BOOSTED)

    @property
    def progressFight(self):
        return 0.0 if self.durationFight == 0 else math_utils.clamp(0.0, 1.0, (BigWorld.serverTime() - self.startTimeFight) / self.durationFight)

    @property
    def progressTurbo(self):
        return 0.0 if self.durationTurbo == 0 else math_utils.clamp(0.0, 1.0, (BigWorld.serverTime() - self.startTimeTurbo) / self.durationTurbo)

    @property
    def isEnoughEnergyToActivate(self):
        if self.isTurboState:
            return self.energyTurbo >= self.params.activeTurboCost
        return self.energyFight >= self.params.activeFightCost if self.isFightState else False

    def isTransition(self, other):
        return self.state != other.state


@ReprInjector.withParent()
class StanceDanceController(VehicleDynamicComponent, IMechanicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):

    def __init__(self):
        super(StanceDanceController, self).__init__()
        self.__params = None
        self.__mechanicPrefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__commandsEvents = createMechanicCommandsEvents(self, withDebug=_LOG_STANCE_DANCE_DEBUG)
        self.__statesEvents = createMechanicStatesEvents(self, withDebug=_LOG_STANCE_DANCE_DEBUG)
        self._initComponent()
        return

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.STANCE_DANCE

    @property
    def commandsEvents(self):
        return self.__commandsEvents

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getMechanicState(self):
        return StanceDanceState.fromComponentStatus(self.abilityState, self.__params)

    def set_abilityState(self, *_):
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__params = None
        self.__commandsEvents.destroy()
        self.__statesEvents.destroy()
        super(StanceDanceController, self).onDestroy()
        return

    def tryUseActiveAbility(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.ACTIVATE)
        state = self.getMechanicState()
        canDoCommand = not state.isEngineDeadState and state.isEnoughEnergyToActivate
        if canDoCommand:
            state = self.getMechanicState()
            stance = STANCE_DANCE_STATE.STANCE_FIGHT if state.isFightState else STANCE_DANCE_STATE.STANCE_TURBO
            self.cell.useActiveAbility(stance)
        return canDoCommand

    def trySwitchStance(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.SWITCH)
        state = self.getMechanicState()
        canDoCommand = not state.isEngineDeadState and not state.isSwitchingState
        if canDoCommand:
            self.cell.switchStance()
        return canDoCommand

    def _onAppearanceReady(self):
        super(StanceDanceController, self)._onAppearanceReady()
        self.__mechanicPrefabSpawner.loadAppearancePrefab()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(StanceDanceController, self)._onComponentAppearanceUpdate(**kwargs)
        self.__statesEvents.updateMechanicState(self.getMechanicState())

    def _collectComponentParams(self, typeDescriptor):
        super(StanceDanceController, self)._collectComponentParams(typeDescriptor)
        self.__params = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)
