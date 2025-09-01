# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/BattleFuryController.py
import BigWorld
import typing
from vehicles.components.vehicle_component import VehicleMechanicPrefabDynamicComponent
from vehicles.mechanics.mechanic_states import createMechanicStatesEvents, IMechanicStatesComponent, IMechanicState
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents
    from typing import Optional, Dict, Any

class BattleFuryState(typing.NamedTuple('BattleFuryState', (('level', int),
 ('maxLevel', int),
 ('startTime', float),
 ('endTime', float))), IMechanicState):

    @classmethod
    def fromComponentStatus(cls, status):
        return cls(status.currentLevel, status.maxLevel, status.timeInterval['startTime'], status.timeInterval['endTime'])

    @property
    def progress(self):
        return max(self.endTime - BigWorld.serverTime(), 0.0) / self.duration if self.level > 0 and self.duration > 0 else 0.0

    @property
    def duration(self):
        return self.endTime - self.startTime

    def isTransition(self, other):
        return self.level != other.level


class BattleFuryController(VehicleMechanicPrefabDynamicComponent, IMechanicStatesComponent):

    def __init__(self):
        super(BattleFuryController, self).__init__()
        self.__statesEvents = createMechanicStatesEvents(self)
        self._initComponent()

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getMechanicState(self):
        return BattleFuryState.fromComponentStatus(self.abilityState)

    def set_abilityState(self, *_):
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__statesEvents.destroy()
        super(BattleFuryController, self).onDestroy()

    def _onAppearanceReady(self):
        super(BattleFuryController, self)._onAppearanceReady()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self):
        self.__statesEvents.updateMechanicState(self.getMechanicState())
