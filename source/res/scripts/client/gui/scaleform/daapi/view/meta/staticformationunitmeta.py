# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationUnitMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class StaticFormationUnitMeta(BaseRallyRoomView):

    def toggleStatusRequest(self):
        self._printOverrideError('toggleStatusRequest')

    def setRankedMode(self, isRanked):
        self._printOverrideError('setRankedMode')

    def showTeamCard(self):
        self._printOverrideError('showTeamCard')

    def as_closeSlotS(self, slotIdx, cost, slotsLabel):
        if self._isDAAPIInited():
            return self.flashObject.as_closeSlot(slotIdx, cost, slotsLabel)

    def as_openSlotS(self, slotIdx, canBeTaken, slotsLabel, compatibleVehiclesCount):
        if self._isDAAPIInited():
            return self.flashObject.as_openSlot(slotIdx, canBeTaken, slotsLabel, compatibleVehiclesCount)

    def as_setOpenedS(self, isOpened, statusLabel):
        if self._isDAAPIInited():
            return self.flashObject.as_setOpened(isOpened, statusLabel)

    def as_setTotalLabelS(self, hasTotalLevelError, totalLevelLabel, totalLevel):
        if self._isDAAPIInited():
            return self.flashObject.as_setTotalLabel(hasTotalLevelError, totalLevelLabel, totalLevel)

    def as_setLegionnairesCountS(self, visible, legionnairesCount):
        if self._isDAAPIInited():
            return self.flashObject.as_setLegionnairesCount(visible, legionnairesCount)

    def as_setHeaderDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setHeaderData(data)

    def as_setTeamIconS(self, icon):
        if self._isDAAPIInited():
            return self.flashObject.as_setTeamIcon(icon)
