# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ConcentrationModeComponent.py
import typing
from collections import namedtuple
import BigWorld
from constants import CONCENTRATION_MODE_STATE
from vehicles.components.vehicle_component import VehicleMechanicPrefabDynamicComponent
from vehicles.mechanics.mechanic_commands import createMechanicCommandsEvents, IMechanicCommandsComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicState, IMechanicStatesComponent, createMechanicStatesEvents
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_commands import IMechanicCommandsEvents
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents

class ConcentrationModeState(namedtuple('ConcentrationModeState', ('state', 'baseTime', 'endTime')), IMechanicState):

    @classmethod
    def fromComponentStatus(cls, status):
        return cls(status.state, status.baseTime, status.endTime)

    @property
    def progress(self):
        return 1.0 - self.timeLeft / self.baseTime if self.baseTime > 0 else 1.0

    @property
    def timeLeft(self):
        return max(0.0, self.endTime - BigWorld.serverTime() if self.endTime >= 0 else self.baseTime)

    def isTransition(self, other):
        return self.state != other.state


class ConcentrationModeComponent(VehicleMechanicPrefabDynamicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):
    DEFAULT_MODE_STATE = ConcentrationModeState(CONCENTRATION_MODE_STATE.IDLE, 0.0, -1.0)

    def __init__(self):
        super(ConcentrationModeComponent, self).__init__()
        self.__commandsEvents = createMechanicCommandsEvents()
        self.__statesEvents = createMechanicStatesEvents(self)
        self._initComponent()

    @property
    def commandsEvents(self):
        return self.__commandsEvents

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getMechanicState(self):
        return ConcentrationModeState.fromComponentStatus(self.status) if self.status else self.DEFAULT_MODE_STATE

    def set_status(self, _):
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__commandsEvents.destroy()
        self.__statesEvents.destroy()
        super(ConcentrationModeComponent, self).onDestroy()

    def tryActivate(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.ACTIVATE)
        if self.getMechanicState().state == CONCENTRATION_MODE_STATE.READY:
            self.cell.tryActivate()

    def _onAppearanceReady(self):
        super(ConcentrationModeComponent, self)._onAppearanceReady()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self):
        self.__statesEvents.updateMechanicState(self.getMechanicState())
