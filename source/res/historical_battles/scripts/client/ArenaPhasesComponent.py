# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/ArenaPhasesComponent.py
import BigWorld
import Event

class ArenaPhasesComponent(BigWorld.DynamicScriptComponent):
    onPhasesUpdate = Event.Event()
    onWavesUpdate = Event.Event()

    def __init__(self):
        super(ArenaPhasesComponent, self).__init__()
        self.onPhasesUpdate(self)

    def canShow(self):
        return self.phasesCount > 0 and self.currentPhase > 0

    def set_phasesCount(self, prev):
        self.onPhasesUpdate(self)

    def set_currentPhase(self, prev):
        self.onPhasesUpdate(self)

    def set_wavesCount(self, prev):
        self.onPhasesUpdate(self)

    def set_currentWave(self, prev):
        self.onPhasesUpdate(self)
        self.onWavesUpdate(self)
