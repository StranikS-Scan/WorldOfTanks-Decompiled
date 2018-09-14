# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CyberSportUnitMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class CyberSportUnitMeta(BaseRallyRoomView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseRallyRoomView
    null
    """

    def toggleFreezeRequest(self):
        """
        :return :
        """
        self._printOverrideError('toggleFreezeRequest')

    def toggleStatusRequest(self):
        """
        :return :
        """
        self._printOverrideError('toggleStatusRequest')

    def showSettingsRoster(self, vaue):
        """
        :param vaue:
        :return :
        """
        self._printOverrideError('showSettingsRoster')

    def resultRosterSlotsSettings(self, value):
        """
        :param value:
        :return :
        """
        self._printOverrideError('resultRosterSlotsSettings')

    def cancelRosterSlotsSettings(self):
        """
        :return :
        """
        self._printOverrideError('cancelRosterSlotsSettings')

    def lockSlotRequest(self, slotIndex):
        """
        :param slotIndex:
        :return :
        """
        self._printOverrideError('lockSlotRequest')

    def as_updateSlotSettingsS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_updateSlotSettings(value) if self._isDAAPIInited() else None

    def as_closeSlotS(self, slotIdx, cost, slotsLabel):
        """
        :param slotIdx:
        :param cost:
        :param slotsLabel:
        :return :
        """
        return self.flashObject.as_closeSlot(slotIdx, cost, slotsLabel) if self._isDAAPIInited() else None

    def as_openSlotS(self, slotIdx, canBeTaken, slotsLabel, compatibleVehiclesCount):
        """
        :param slotIdx:
        :param canBeTaken:
        :param slotsLabel:
        :param compatibleVehiclesCount:
        :return :
        """
        return self.flashObject.as_openSlot(slotIdx, canBeTaken, slotsLabel, compatibleVehiclesCount) if self._isDAAPIInited() else None

    def as_lockUnitS(self, isLocked, slotsLabel):
        """
        :param isLocked:
        :param slotsLabel:
        :return :
        """
        return self.flashObject.as_lockUnit(isLocked, slotsLabel) if self._isDAAPIInited() else None

    def as_setOpenedS(self, isOpened, statusLabel):
        """
        :param isOpened:
        :param statusLabel:
        :return :
        """
        return self.flashObject.as_setOpened(isOpened, statusLabel) if self._isDAAPIInited() else None

    def as_setTotalLabelS(self, hasTotalLevelError, totalLevelLabel, totalLevel):
        """
        :param hasTotalLevelError:
        :param totalLevelLabel:
        :param totalLevel:
        :return :
        """
        return self.flashObject.as_setTotalLabel(hasTotalLevelError, totalLevelLabel, totalLevel) if self._isDAAPIInited() else None

    def as_setPlayerCountLblS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setPlayerCountLbl(value) if self._isDAAPIInited() else None
