# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CyberSportUnitMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class CyberSportUnitMeta(BaseRallyRoomView):

    def toggleFreezeRequest(self):
        self._printOverrideError('toggleFreezeRequest')

    def toggleStatusRequest(self):
        self._printOverrideError('toggleStatusRequest')

    def showSettingsRoster(self, vaue):
        self._printOverrideError('showSettingsRoster')

    def resultRosterSlotsSettings(self, value):
        self._printOverrideError('resultRosterSlotsSettings')

    def cancelRosterSlotsSettings(self):
        self._printOverrideError('cancelRosterSlotsSettings')

    def lockSlotRequest(self, slotIndex):
        self._printOverrideError('lockSlotRequest')

    def as_updateSlotSettingsS(self, value):
        """
        :param value: Represented by Array (AS)
        """
        return self.flashObject.as_updateSlotSettings(value) if self._isDAAPIInited() else None

    def as_closeSlotS(self, slotIdx, cost, slotsLabel):
        return self.flashObject.as_closeSlot(slotIdx, cost, slotsLabel) if self._isDAAPIInited() else None

    def as_openSlotS(self, slotIdx, canBeTaken, slotsLabel, compatibleVehiclesCount):
        return self.flashObject.as_openSlot(slotIdx, canBeTaken, slotsLabel, compatibleVehiclesCount) if self._isDAAPIInited() else None

    def as_lockUnitS(self, isLocked, slotsLabel):
        """
        :param slotsLabel: Represented by Array (AS)
        """
        return self.flashObject.as_lockUnit(isLocked, slotsLabel) if self._isDAAPIInited() else None

    def as_setOpenedS(self, isOpened, statusLabel):
        return self.flashObject.as_setOpened(isOpened, statusLabel) if self._isDAAPIInited() else None

    def as_setTotalLabelS(self, hasTotalLevelError, totalLevelLabel, totalLevel):
        return self.flashObject.as_setTotalLabel(hasTotalLevelError, totalLevelLabel, totalLevel) if self._isDAAPIInited() else None

    def as_setPlayerCountLblS(self, value):
        return self.flashObject.as_setPlayerCountLbl(value) if self._isDAAPIInited() else None
