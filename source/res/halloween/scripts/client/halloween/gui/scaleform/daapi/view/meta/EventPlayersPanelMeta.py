# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/meta/EventPlayersPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventPlayersPanelMeta(BaseDAAPIComponent):

    def acceptSquad(self, sessionID):
        self._printOverrideError('acceptSquad')

    def addToSquad(self, sessionID):
        self._printOverrideError('addToSquad')

    def as_setPlayerPanelInfoS(self, data):
        return self.flashObject.as_setPlayerPanelInfo(data) if self._isDAAPIInited() else None

    def as_clearPlayerPanelS(self):
        return self.flashObject.as_clearPlayerPanel() if self._isDAAPIInited() else None

    def as_setPlayerPanelHpS(self, vehID, hpMax, hpCurrent):
        return self.flashObject.as_setPlayerPanelHp(vehID, hpMax, hpCurrent) if self._isDAAPIInited() else None

    def as_setPlayerDeadS(self, vehID):
        return self.flashObject.as_setPlayerDead(vehID) if self._isDAAPIInited() else None

    def as_setPlayerPanelCountSoulsS(self, vehID, countSouls):
        return self.flashObject.as_setPlayerPanelCountSouls(vehID, countSouls) if self._isDAAPIInited() else None

    def as_setCollectorGoalS(self, goal):
        return self.flashObject.as_setCollectorGoal(goal) if self._isDAAPIInited() else None

    def as_setCollectorNeedValueS(self, value):
        return self.flashObject.as_setCollectorNeedValue(value) if self._isDAAPIInited() else None

    def as_setChatCommandS(self, vehicleID, chatCommand, chatCommandFlags):
        return self.flashObject.as_setChatCommand(vehicleID, chatCommand, chatCommandFlags) if self._isDAAPIInited() else None
