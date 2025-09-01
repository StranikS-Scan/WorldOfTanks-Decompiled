# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/StanceDanceController.py
import BigWorld
import typing
import math_utils
from constants import STANCE_DANCE_STATE
from items.components.shared_components import StanceDanceParams
from vehicles.mechanics.mechanic_commands import createMechanicCommandsEvents
from vehicles.components.vehicle_component import VehicleMechanicPrefabDynamicComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import createMechanicStatesEvents, IMechanicStatesComponent, IMechanicState
if typing.TYPE_CHECKING:
    from typing import Any
    from vehicles.mechanics.mechanic_commands import IMechanicCommandsEvents
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents

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

    def __repr__(self):
        return 'StanceDanceState<isTurboState={}, isActiveTurboState={}, energyTurbo={}, durationTurbo={}, progressTurbo={}, \nisFightState={}, isActiveFightState={}, energyFight={}, durationFight={}, progressFight={}, \nisSwitchingState={}, durationSwitch={}, isGainingEnergy={}, isGainingEnergyBoosted={}, \nparams={}>'.format(self.isTurboState, self.isActiveTurboState, self.energyTurbo, self.durationTurbo, self.progressTurbo, self.isFightState, self.isActiveFightState, self.energyFight, self.durationFight, self.progressFight, self.isSwitchingState, self.durationSwitch, self.isGainingEnergy, self.isGainingEnergyBoosted, self.params)


class StanceDanceController(VehicleMechanicPrefabDynamicComponent, IMechanicStatesComponent):

    def __init__(self):
        super(StanceDanceController, self).__init__()
        self.__params = None
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
        self.__params = self.entity.typeDescriptor.mechanicsParams[StanceDanceParams.MECHANICS_NAME]
        self.__statesEvents.processStatePrepared()
        super(StanceDanceController, self)._onAppearanceReady()

    def _onComponentAppearanceUpdate(self):
        self.__statesEvents.updateMechanicState(self.getMechanicState())
