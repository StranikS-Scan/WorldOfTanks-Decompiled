# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PowerModeController.py
import typing
from collections import namedtuple
import BigWorld
from constants import POWER_MODE_STATE
from gui.battle_control.battle_constants import VEHICLE_UPDATE_INTERVAL
from math_utils import clamp01
from vehicles.components.vehicle_component import VehicleMechanicPrefabDynamicComponent
from vehicles.mechanics.mechanic_states import IMechanicState, IMechanicStatesComponent, createMechanicStatesEvents
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents

class PowerModeState(namedtuple('PowerModeState', ('state', 'directionChangeTime', 'lastProgress', 'progressSpeed')), IMechanicState):

    @classmethod
    def fromComponentStatus(cls, status, timeInfo=None):
        progressSpeed = 0
        if timeInfo:
            currentTime = timeInfo.modeDuration if status.state in POWER_MODE_STATE.ACTIVE_MODES else timeInfo.modeThreshold
            progressSpeed = status.directionFactor / currentTime
        return cls(status.state, status.stateActivationTime, status.powerProgress, progressSpeed)

    @property
    def activeProgress(self):
        return self.progress if self.state in POWER_MODE_STATE.ACTIVE_MODES else 0.0

    @property
    def progress(self):
        if self.state in POWER_MODE_STATE.STATIC_MODES:
            return self.lastProgress
        dt = max(BigWorld.serverTime() - self.directionChangeTime, 0.0)
        return clamp01(self.lastProgress + dt * self.progressSpeed)

    def isTransition(self, other):
        return self.state != other.state


class PowerModeController(VehicleMechanicPrefabDynamicComponent, IMechanicStatesComponent):
    DEFAULT_MODE_STATE = PowerModeState(POWER_MODE_STATE.NOT_ACTIVE, 0.0, 0.0, 0.0)

    def __init__(self):
        super(PowerModeController, self).__init__()
        self.__mechanicState = self.DEFAULT_MODE_STATE
        self.__statesEvents = createMechanicStatesEvents(self, VEHICLE_UPDATE_INTERVAL)
        self._initComponent()

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getMechanicState(self):
        return self.__mechanicState

    def set_stateStatus(self, _):
        self._updateComponentAppearance()

    def set_timeInfo(self, _):
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__statesEvents.destroy()
        super(PowerModeController, self).onDestroy()

    def _onAppearanceReady(self):
        super(PowerModeController, self)._onAppearanceReady()
        self.__updateMechanicState()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self):
        self.__updateMechanicState()
        self.__statesEvents.updateMechanicState(self.getMechanicState())

    def __updateMechanicState(self):
        self.__mechanicState = PowerModeState.fromComponentStatus(status=self.stateStatus, timeInfo=self.timeInfo) if self.stateStatus else self.DEFAULT_MODE_STATE
