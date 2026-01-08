# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TargetDesignatorController.py
import typing
import BigWorld
from constants import TARGET_DESIGNATOR_STATE as STATE
from gui.shared.utils.decorators import ReprInjector
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.mechanics.common import IMechanicComponent
from vehicles.mechanics.mechanic_commands import IMechanicCommandsComponent, createMechanicCommandsEvents
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
from vehicles.mechanics.mechanic_states import IMechanicState, IMechanicStatesComponent, createMechanicStatesEvents
if typing.TYPE_CHECKING:
    from typing import Optional
    from items.components.shared_components import TargetDesignatorParams
    from vehicles.mechanics.mechanic_commands import IMechanicCommandsEvents
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents

@ReprInjector.simple('state', 'startTime', 'endTime')
class TargetDesignatorState(IMechanicState):
    __slots__ = ('state', 'params', 'baseTime', 'startTime', 'endTime')

    def __init__(self, state, params, startTime=0.0, endTime=0.0):
        self.state = state
        self.params = params
        self.baseTime = endTime - startTime
        self.startTime = startTime
        self.endTime = endTime

    def timeLeft(self):
        if self.state == STATE.PRE_BATTLE:
            if self.params is not None:
                return self.params.deployTime
            return 0
        else:
            return max(0.0, self.endTime - BigWorld.serverTime() if self.endTime > 0 else self.baseTime)

    def baseTimeLeft(self):
        return max(0.0, self.startTime + self.baseTime - BigWorld.serverTime() if self.endTime > 0 else self.baseTime)

    def progress(self, timeLeft):
        return 1.0 - timeLeft / self.baseTime if self.baseTime > 0 else 1.0

    def isTransition(self, other):
        return self.state != other.state


@ReprInjector.withParent()
class TargetDesignatorController(VehicleDynamicComponent, IMechanicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):

    def __init__(self):
        super(TargetDesignatorController, self).__init__()
        self.__mechanicPrefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__commandsEvents = createMechanicCommandsEvents(self)
        self.__statesEvents = createMechanicStatesEvents(self)
        self.__params = None
        self.__state = self.__updateState()
        self._initComponent()
        return

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.TARGET_DESIGNATOR

    @property
    def commandsEvents(self):
        return self.__commandsEvents

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getComponentParams(self):
        return self.__params

    def getMechanicState(self):
        return self.__state

    def set_abilityState(self, _):
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__params = None
        self.__commandsEvents.destroy()
        self.__statesEvents.destroy()
        super(TargetDesignatorController, self).onDestroy()
        return

    def tryActivate(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.ACTIVATE)
        if self.__state.state != STATE.READY:
            return
        self.cell.tryActivate()

    def _onAppearanceReady(self):
        super(TargetDesignatorController, self)._onAppearanceReady()
        self.__state = self.__updateState()
        self.__mechanicPrefabSpawner.loadAppearancePrefab()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(TargetDesignatorController, self)._onComponentAppearanceUpdate(**kwargs)
        self.__state = newState = self.__updateState()
        self.__statesEvents.updateMechanicState(newState)

    def _collectComponentParams(self, typeDescriptor):
        super(TargetDesignatorController, self)._collectComponentParams(typeDescriptor)
        self.__params = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)

    def __updateState(self):
        return TargetDesignatorState(STATE.PRE_BATTLE, self.__params) if self.abilityState is None else TargetDesignatorState(self.abilityState.state, self.__params, self.abilityState.startTime, self.abilityState.endTime)
