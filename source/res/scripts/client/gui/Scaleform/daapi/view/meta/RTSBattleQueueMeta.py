# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RTSBattleQueueMeta.py
from gui.Scaleform.daapi.view.lobby.battle_queue.base_queue import BattleQueueBase

class RTSBattleQueueMeta(BattleQueueBase):

    def onSwitchVehicleClick(self):
        self._printOverrideError('onSwitchVehicleClick')

    def as_showSwitchVehicleS(self, data):
        return self.flashObject.as_showSwitchVehicle(data) if self._isDAAPIInited() else None

    def as_hideSwitchVehicleS(self):
        return self.flashObject.as_hideSwitchVehicle() if self._isDAAPIInited() else None

    def as_setRTSDPS(self, dataProvider):
        return self.flashObject.as_setRTSDP(dataProvider) if self._isDAAPIInited() else None
