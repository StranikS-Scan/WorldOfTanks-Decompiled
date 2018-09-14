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
        """
        :param data: Represented by FortClanBattleRoomVO (AS)
        """
        return self.flashObject.as_setBattleRoomData(data) if self._isDAAPIInited() else None

    def as_updateReadyStatusS(self, mineValue, enemyValue):
        return self.flashObject.as_updateReadyStatus(mineValue, enemyValue) if self._isDAAPIInited() else None

    def as_setConfigureButtonStateS(self, data):
        """
        :param data: Represented by ActionButtonVO (AS)
        """
        return self.flashObject.as_setConfigureButtonState(data) if self._isDAAPIInited() else None

    def as_setTimerDeltaS(self, data):
        """
        :param data: Represented by ClanBattleTimerVO (AS)
        """
        return self.flashObject.as_setTimerDelta(data) if self._isDAAPIInited() else None

    def as_updateDirectionsS(self, data):
        """
        :param data: Represented by ConnectedDirectionsVO (AS)
        """
        return self.flashObject.as_updateDirections(data) if self._isDAAPIInited() else None

    def as_setDirectionS(self, value, animationNotAvailable):
        return self.flashObject.as_setDirection(value, animationNotAvailable) if self._isDAAPIInited() else None

    def as_setReservesEnabledS(self, data):
        """
        :param data: Represented by Array (AS)
        """
        return self.flashObject.as_setReservesEnabled(data) if self._isDAAPIInited() else None

    def as_setReservesDataS(self, reservesData):
        """
        :param reservesData: Represented by Vector.<DeviceSlotVO> (AS)
        """
        return self.flashObject.as_setReservesData(reservesData) if self._isDAAPIInited() else None

    def as_setOpenedS(self, buttonLabel, statusLabel, tooltipLabel):
        return self.flashObject.as_setOpened(buttonLabel, statusLabel, tooltipLabel) if self._isDAAPIInited() else None

    def as_setTableHeaderS(self, data):
        """
        :param data: Represented by Vector.<NormalSortingBtnVO> (AS)
        """
        return self.flashObject.as_setTableHeader(data) if self._isDAAPIInited() else None
