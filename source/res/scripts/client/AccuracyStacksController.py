# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AccuracyStacksController.py
import typing
import BigWorld
from gui.shared.utils.decorators import ReprInjector
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.mechanics.common import IMechanicComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
from vehicles.mechanics.mechanic_states import IMechanicState, IMechanicStatesComponent, createMechanicStatesEvents
if typing.TYPE_CHECKING:
    from typing import Any, Optional
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents

@ReprInjector.simple('level', 'startTime', 'endTime', 'timeElapsed')
class AccuracyStacksState(typing.NamedTuple('AccuracyStacksState', (('level', int),
 ('maxLevel', int),
 ('startTime', float),
 ('endTime', float),
 ('isGainingActive', bool),
 ('duration', float),
 ('timeElapsed', float),
 ('speedThreshold', float))), IMechanicState):

    @classmethod
    def fromComponentStatus(cls, status, stackDuration, speedThreshold):
        endTime = status.timeNextGain['endTime']
        return cls(status.curLevel, status.maxLevel, status.timeNextGain['startTime'], endTime, endTime > 0, stackDuration, status.timeElapsed, speedThreshold)

    @property
    def progress(self):
        if self.duration == 0:
            return 0.0
        timeElapsed = self.timeElapsed
        if self.isGainingActive:
            timeElapsed += BigWorld.serverTime() - self.startTime
        return min(timeElapsed / self.duration, 1.0)

    def isTransition(self, other):
        return self.level != other.level or self.isGainingActive != other.isGainingActive


@ReprInjector.withParent()
class AccuracyStacksController(VehicleDynamicComponent, IMechanicComponent, IMechanicStatesComponent):

    def __init__(self):
        super(AccuracyStacksController, self).__init__()
        self.__stackDuration = 0.0
        self.__speedThreshold = 0.0
        self.__mechanicPrefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__statesEvents = createMechanicStatesEvents(self)
        self._initComponent()

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.ACCURACY_STACKS

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getComponentParams(self):
        return (self.__stackDuration, self.__speedThreshold)

    def getMechanicState(self):
        return AccuracyStacksState.fromComponentStatus(self.abilityState, self.__stackDuration, self.__speedThreshold)

    def set_abilityState(self, *_):
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__statesEvents.destroy()
        super(AccuracyStacksController, self).onDestroy()

    def _onAppearanceReady(self):
        super(AccuracyStacksController, self)._onAppearanceReady()
        self.__mechanicPrefabSpawner.loadAppearancePrefab()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(AccuracyStacksController, self)._onComponentAppearanceUpdate(**kwargs)
        self.__statesEvents.updateMechanicState(self.getMechanicState())

    def _collectComponentParams(self, typeDescriptor):
        super(AccuracyStacksController, self)._collectComponentParams(typeDescriptor)
        mechanicParams = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)
        self.__stackDuration = mechanicParams.gainTime
        self.__speedThreshold = mechanicParams.gainMaxSpd
