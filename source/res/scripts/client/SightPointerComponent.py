# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SightPointerComponent.py
from __future__ import absolute_import, division
import typing
import BigWorld
from constants import SIGHT_POINTER_STATE, SIGHT_POINTER_COMMON_CONSTANTS
from gui.shared.utils.decorators import ReprInjector
from items.vehicles import VehicleDescriptor
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.mechanics.common import IMechanicComponent
from vehicles.mechanics.mechanic_commands import IMechanicCommandsComponent, IMechanicCommandsEvents, createMechanicCommandsEvents
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
from vehicles.mechanics.generic_mechanics.sight_pointer import createSightPointerStatesEvents
from vehicles.mechanics.mechanic_states import IMechanicState, IMechanicStatesComponent, IMechanicStatesEvents

class SightPointerState(typing.NamedTuple('SightPointerState', (('state', SIGHT_POINTER_STATE),
 ('nextState', SIGHT_POINTER_STATE),
 ('baseTime', float),
 ('endTime', float),
 ('vehiclesUnderScan', bool),
 ('angle', float),
 ('distance', float),
 ('stage', int))), IMechanicState):

    def canUseAbility(self):
        return self.state == SIGHT_POINTER_STATE.READY

    @property
    def timeLeft(self):
        return max(0.0, self.endTime - BigWorld.serverTime()) if self.endTime > 0 else 0.0

    @property
    def progress(self):
        if self.endTime <= 0 or self.baseTime <= 0:
            return 0.0
        duration = self.endTime - self.baseTime
        if duration <= 0:
            return 1.0
        elapsed = BigWorld.serverTime() - self.baseTime
        return min(1.0, max(0.0, elapsed / duration))

    def isTransition(self, other):
        return self.state != other.state or self.nextState != other.nextState


@ReprInjector.withParent()
class SightPointerComponent(VehicleDynamicComponent, IMechanicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):

    def __init__(self):
        super(SightPointerComponent, self).__init__()
        self.__commandsEvents = createMechanicCommandsEvents(self)
        self.__statesEvents = createSightPointerStatesEvents(self)
        self.__mechanicPrefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__mechanicParams = None
        self.__baseTime = -1.0
        self.__maxAngle = 0.0
        self.__minAngle = 0.0
        self._initComponent()
        return

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.SIGHT_POINTER

    @property
    def commandsEvents(self):
        return self.__commandsEvents

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getMechanicState(self):
        baseTime = -1.0
        endTime = 0.0
        src = SIGHT_POINTER_STATE.DISABLED
        dst = SIGHT_POINTER_STATE.DISABLED
        vehiclesUnderScan = False
        angle = 0.0
        distance = 0.0
        stage = 0
        if self.status:
            baseTime = self.status.baseTime
            endTime = self.status.endTime
            src = self.status.state
            dst = self.status.nextState
            vehiclesUnderScan = bool(self.abilityInfo.vehiclesUnderScan)
            angle = self.abilityInfo.angle
            distance = self.abilityInfo.distance
            stage = self.abilityInfo.stage
            if src in (SIGHT_POINTER_STATE.DISABLED, SIGHT_POINTER_STATE.COOLDOWN):
                self.__baseTime = self.status.baseTime
                endTime += SIGHT_POINTER_COMMON_CONSTANTS.ANIMATION_DELAY
                if self.__baseTime > 0:
                    baseTime = self.__baseTime
            elif src == SIGHT_POINTER_STATE.PREPARING and self.__baseTime > 0:
                baseTime = self.__baseTime
        return SightPointerState(state=src, nextState=dst, baseTime=baseTime, endTime=endTime, vehiclesUnderScan=vehiclesUnderScan, angle=angle, distance=distance, stage=stage)

    def set_abilityInfo(self, _):
        self._updateComponentAppearance()

    def set_status(self, _):
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__commandsEvents.destroy()
        self.__statesEvents.destroy()
        super(SightPointerComponent, self).onDestroy()

    def getComponentParams(self):
        return self.__mechanicParams

    def tryActivate(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.ACTIVATE)
        if self.getMechanicState().state == SIGHT_POINTER_STATE.READY:
            self.cell.tryActivate()

    def tryDeactivate(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.DEACTIVATE)
        state = self.getMechanicState()
        if state.state == SIGHT_POINTER_STATE.ACTIVE:
            if BigWorld.serverTime() - state.baseTime < SIGHT_POINTER_COMMON_CONSTANTS.MIN_ACTIVE_DURATION:
                return
            self.cell.tryDeactivate()

    def alternateOnState(self):
        if self.getMechanicState().state == SIGHT_POINTER_STATE.ACTIVE:
            self.tryDeactivate()
        else:
            self.tryActivate()

    def _onAppearanceReady(self):
        super(SightPointerComponent, self)._onAppearanceReady()
        self.__applyComponentParams()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(SightPointerComponent, self)._onComponentAppearanceUpdate(**kwargs)
        self.__statesEvents.updateMechanicState(self.getMechanicState())

    def _collectComponentParams(self, typeDescriptor):
        super(SightPointerComponent, self)._collectComponentParams(typeDescriptor)
        self.__mechanicParams = params = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)
        self.__maxAngle = params.sightPointerStages[0].angle
        lastActiveIdx = min(params.activeStages, len(params.sightPointerStages)) - 1
        self.__minAngle = params.sightPointerStages[lastActiveIdx].angle

    def __applyComponentParams(self):
        self.__statesEvents.updateComponentParams(self.__maxAngle, self.__minAngle)
