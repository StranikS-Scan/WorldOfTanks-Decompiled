# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/meta/HBRespawnMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HBRespawnMeta(BaseDAAPIComponent):

    def onPickVehicle(self, id):
        self._printOverrideError('onPickVehicle')

    def onSelectVehicle(self):
        self._printOverrideError('onSelectVehicle')

    def as_updateGoalTimeS(self, value):
        return self.flashObject.as_updateGoalTime(value) if self._isDAAPIInited() else None

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setTimerDataS(self, data):
        return self.flashObject.as_setTimerData(data) if self._isDAAPIInited() else None

    def as_setVisibilityS(self, isVisible, isRespawn=False):
        return self.flashObject.as_setVisibility(isVisible, isRespawn) if self._isDAAPIInited() else None
