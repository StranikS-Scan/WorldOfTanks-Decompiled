# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleVehicleSelectorMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleVehicleSelectorMeta(BaseDAAPIComponent):

    def onVehicleSelect(self, id):
        self._printOverrideError('onVehicleSelect')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setTimerS(self, time):
        return self.flashObject.as_setTimer(time) if self._isDAAPIInited() else None

    def as_setTeamMissionsVehiclesS(self, data):
        return self.flashObject.as_setTeamMissionsVehicles(data) if self._isDAAPIInited() else None

    def as_setTabsSelectedIndexS(self, index):
        return self.flashObject.as_setTabsSelectedIndex(index) if self._isDAAPIInited() else None

    def as_setHelpVisibleS(self, visible):
        return self.flashObject.as_setHelpVisible(visible) if self._isDAAPIInited() else None
