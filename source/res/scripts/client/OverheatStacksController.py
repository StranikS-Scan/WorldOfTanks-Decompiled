# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/OverheatStacksController.py
import BigWorld
import typing
from constants import OVERHEAT_GAIN_STATE as STATE
from items.components.shared_components import OverheatStacksParams
from math_utils import clamp
from vehicles.components.vehicle_component import VehicleMechanicPrefabDynamicComponent
from vehicles.mechanics.mechanic_states import createMechanicStatesEvents, IMechanicStatesComponent, IMechanicState
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_states import MechanicStatesEvents

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


class OverheatStacksController(VehicleMechanicPrefabDynamicComponent, IMechanicStatesComponent):

    def __init__(self):
        super(OverheatStacksController, self).__init__()
        self.__params = None
        self.__statesEvents = createMechanicStatesEvents(self)
        self._initComponent()
        return

    @property
    def statesEvents(self):
        return self.__statesEvents

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
        self.__params = self.entity.typeDescriptor.mechanicsParams[OverheatStacksParams.MECHANICS_NAME]
        self.__statesEvents.processStatePrepared()
        super(OverheatStacksController, self)._onAppearanceReady()

    def _onComponentAppearanceUpdate(self):
        self.__statesEvents.updateMechanicState(self.getMechanicState())
