# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortClanBattleRoomMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class FortClanBattleRoomMeta(BaseRallyRoomView):

    def onTimerAlert(self):
        self._printOverrideError('onTimerAlert')

    def openConfigureWindow(self):
        self._printOverrideError('openConfigureWindow')

    def toggleRoomStatus(self):
        self._printOverrideError('toggleRoomStatus')

    def as_updateTeamHeaderTextS(self, value):
        return self.flashObject.as_updateTeamHeaderText(value) if self._isDAAPIInited() else None

    def as_setBattleRoomDataS(self, data):
        return self.flashObject.as_setBattleRoomData(data) if self._isDAAPIInited() else None

    def as_updateReadyStatusS(self, mineValue, enemyValue):
        return self.flashObject.as_updateReadyStatus(mineValue, enemyValue) if self._isDAAPIInited() else None

    def as_updateReadyDirectionsS(self, value):
        return self.flashObject.as_updateReadyDirections(value) if self._isDAAPIInited() else None

    def as_setConfigureButtonStateS(self, data):
        return self.flashObject.as_setConfigureButtonState(data) if self._isDAAPIInited() else None

    def as_setTimerDeltaS(self, data):
        return self.flashObject.as_setTimerDelta(data) if self._isDAAPIInited() else None

    def as_setDirectionS(self, value, animationNotAvailable):
        return self.flashObject.as_setDirection(value, animationNotAvailable) if self._isDAAPIInited() else None

    def as_setReservesEnabledS(self, data):
        return self.flashObject.as_setReservesEnabled(data) if self._isDAAPIInited() else None

    def as_setReservesDataS(self, reservesData):
        return self.flashObject.as_setReservesData(reservesData) if self._isDAAPIInited() else None

    def as_setOpenedS(self, buttonLabel, statusLabel, tooltipLabel):
        return self.flashObject.as_setOpened(buttonLabel, statusLabel, tooltipLabel) if self._isDAAPIInited() else None

    def as_setTableHeaderS(self, data):
        return self.flashObject.as_setTableHeader(data) if self._isDAAPIInited() else None
