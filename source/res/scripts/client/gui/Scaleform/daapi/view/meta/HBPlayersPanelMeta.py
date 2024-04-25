# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HBPlayersPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HBPlayersPanelMeta(BaseDAAPIComponent):

    def acceptSquad(self, sessionID):
        self._printOverrideError('acceptSquad')

    def addToSquad(self, sessionID):
        self._printOverrideError('addToSquad')

    def switchToOtherPlayer(self, vehicleID):
        self._printOverrideError('switchToOtherPlayer')

    def as_getDPS(self):
        return self.flashObject.as_getDP() if self._isDAAPIInited() else None

    def as_setPlayerHpS(self, vehID, hpMax, hpCurrent, isSkipAnimation=False):
        return self.flashObject.as_setPlayerHp(vehID, hpMax, hpCurrent, isSkipAnimation) if self._isDAAPIInited() else None

    def as_setPlayerCountLivesS(self, vehID, countLives):
        return self.flashObject.as_setPlayerCountLives(vehID, countLives) if self._isDAAPIInited() else None

    def as_setChatCommandS(self, vehID, chatCommand, chatCommandFlags):
        return self.flashObject.as_setChatCommand(vehID, chatCommand, chatCommandFlags) if self._isDAAPIInited() else None

    def as_setChatCommandsVisibilityS(self, value):
        return self.flashObject.as_setChatCommandsVisibility(value) if self._isDAAPIInited() else None

    def as_setPlayersSwitchingAllowedS(self, isAllowed):
        return self.flashObject.as_setPlayersSwitchingAllowed(isAllowed) if self._isDAAPIInited() else None
