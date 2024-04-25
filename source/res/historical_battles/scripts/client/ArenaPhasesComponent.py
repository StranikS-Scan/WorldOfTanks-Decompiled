# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/ArenaPhasesComponent.py
import BigWorld
import Event

class ArenaPhasesComponent(BigWorld.DynamicScriptComponent):
    onPhasesUpdate = Event.Event()

    def __init__(self):
        super(ArenaPhasesComponent, self).__init__()
        self._update()

    def canShow(self):
        return self.phasesCount > 0 and self.currentPhase > 0

    def set_phasesCount(self, prev):
        self._update()

    def set_currentPhase(self, prev):
        self._update()

    def _update(self):
        self.onPhasesUpdate(self)
