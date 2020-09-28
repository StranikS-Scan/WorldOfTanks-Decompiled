# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventPlayersPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventPlayersPanelMeta(BaseDAAPIComponent):

    def acceptSquad(self, sessionID):
        self._printOverrideError('acceptSquad')

    def addToSquad(self, sessionID):
        self._printOverrideError('addToSquad')

    def as_setPlayersPanelDataS(self, data):
        return self.flashObject.as_setPlayersPanelData(data) if self._isDAAPIInited() else None

    def as_setPlayerPanelInfoS(self, data):
        return self.flashObject.as_setPlayerPanelInfo(data) if self._isDAAPIInited() else None

    def as_setPlayerPanelHpS(self, vehID, hpCurrent):
        return self.flashObject.as_setPlayerPanelHp(vehID, hpCurrent) if self._isDAAPIInited() else None

    def as_setPlayerLivesS(self, vehID, lives):
        return self.flashObject.as_setPlayerLives(vehID, lives) if self._isDAAPIInited() else None

    def as_setPlayerDeadS(self, vehID):
        return self.flashObject.as_setPlayerDead(vehID) if self._isDAAPIInited() else None

    def as_setPlayerResurrectS(self, vehID, isResurrect):
        return self.flashObject.as_setPlayerResurrect(vehID, isResurrect) if self._isDAAPIInited() else None

    def as_setPlayerPanelCountPointsS(self, vehID, count):
        return self.flashObject.as_setPlayerPanelCountPoints(vehID, count) if self._isDAAPIInited() else None
