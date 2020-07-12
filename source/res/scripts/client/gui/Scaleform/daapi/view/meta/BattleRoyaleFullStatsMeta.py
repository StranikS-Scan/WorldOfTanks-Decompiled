# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleRoyaleFullStatsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleRoyaleFullStatsMeta(BaseDAAPIComponent):

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_updateScoreS(self, alive, destroyed, squads):
        return self.flashObject.as_updateScore(alive, destroyed, squads) if self._isDAAPIInited() else None

    def as_updateNationsVehiclesCounterS(self, data):
        return self.flashObject.as_updateNationsVehiclesCounter(data) if self._isDAAPIInited() else None
