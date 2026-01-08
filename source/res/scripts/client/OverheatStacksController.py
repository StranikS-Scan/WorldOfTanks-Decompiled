# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/OverheatStacksController.py
import typing
import BigWorld
from constants import OVERHEAT_GAIN_STATE as STATE
from gui.shared.utils.decorators import ReprInjector
from math_utils import clamp
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.mechanics.common import IMechanicComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
from vehicles.mechanics.mechanic_states import createMechanicStatesEvents, IMechanicStatesComponent, IMechanicState
if typing.TYPE_CHECKING:
    from items.components.shared_components import OverheatStacksParams
    from vehicles.mechanics.mechanic_states import MechanicStatesEvents
_LOG_OVERHEAT_STACKS_DEBUG = False

@ReprInjector.simple('level', 'gainState', 'startTime', 'endTime', 'delayTimerElapsed', 'stackTimeElapsed')
class OverheatStacksState(typing.NamedTuple('OverheatStacksState', (('level', int),
 ('gainState', STATE),
 ('startTime', int),
 ('endTime', int),
 ('delayTimerElapsed', float),
 ('stackTimeElapsed', float),
 ('delayTimerDuration', float),
 ('stackDuration', float),
 ('dmgLevelBonus', float),
 ('speedThreshold', float),
 ('maxLevel', int),
 ('heatingTime', float),
 ('coolingTime', float))), IMechanicState):

    @classmethod
    def fromComponentStatus(cls, curLevel, gainState, timeElapsed, delayTimerElapsed, timeNextGain, params):
        return cls(curLevel, gainState, timeNextGain['startTime'] if timeNextGain is not None else 0, timeNextGain['endTime'] if timeNextGain is not None else 0, delayTimerElapsed if delayTimerElapsed is not None else 0.0, timeElapsed if timeElapsed is not None else 0.0, params.delayTimerDuration if params else 0.0, params.gainTime if params else 0.0, params.dmgLevelBonus if params else 0.0, params.gainMaxSpd if params else 0.0, params.levelMax if params else 0, params.heatingTime if params else 0.0, params.coolingTime if params else 0.0)

    @property
    def progress(self):
        timeElapsed = self.stackTimeElapsed
        if self.gainState == STATE.STACK_GAIN:
            timeElapsed += BigWorld.serverTime() - self.startTime
        return min(timeElapsed / self.stackDuration, 1.0)

    @property
    def delayTimerProgress(self):
        if self.gainState & STATE.DT_PROGRESS_FULL:
            return 1.0
        if self.gainState & STATE.DT_PROGRESS_ZERO:
            return 0.0
        direction = 0.0
        if self.gainState == STATE.DT_GAIN:
            direction = 1.0
        elif self.gainState == STATE.DT_LOOSE:
            direction = -1.0
        initProgress = self.delayTimerElapsed / self.delayTimerDuration
        timeProgress = direction * (BigWorld.serverTime() - self.startTime) / self.delayTimerDuration
        return clamp(0.0, 1.0, initProgress + timeProgress)

    def isTransition(self, other):
        return self.level != other.level or self.gainState != other.gainState


@ReprInjector.withParent()
class OverheatStacksController(VehicleDynamicComponent, IMechanicComponent, IMechanicStatesComponent):

    def __init__(self):
        super(OverheatStacksController, self).__init__()
        self.__params = None
        self.__mechanicPrefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__statesEvents = createMechanicStatesEvents(self, withDebug=_LOG_OVERHEAT_STACKS_DEBUG)
        self._initComponent()
        return

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.OVERHEAT_STACKS

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getComponentParams(self):
        return self.__params

    def getMechanicState(self):
        return OverheatStacksState.fromComponentStatus(self.curLevel, self.gainState, self.timeElapsed, self.delayTimerElapsed, self.timeNextGain, self.__params)

    def onDestroy(self):
        self.__params = None
        self.__statesEvents.destroy()
        super(OverheatStacksController, self).onDestroy()
        return

    def set_curLevel(self, *_, **__):
        self._updateComponentAppearance()

    def set_gainState(self, *_, **__):
        self._updateComponentAppearance()

    def set_timeElapsed(self, *_, **__):
        self._updateComponentAppearance()

    def set_delayTimerElapsed(self, *_, **__):
        self._updateComponentAppearance()

    def set_timeNextGain(self, *_, **__):
        self._updateComponentAppearance()

    def _onAppearanceReady(self):
        super(OverheatStacksController, self)._onAppearanceReady()
        self.__mechanicPrefabSpawner.loadAppearancePrefab()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(OverheatStacksController, self)._onComponentAppearanceUpdate(**kwargs)
        self.__statesEvents.updateMechanicState(self.getMechanicState())

    def _collectComponentParams(self, typeDescriptor):
        super(OverheatStacksController, self)._collectComponentParams(typeDescriptor)
        self.__params = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)
