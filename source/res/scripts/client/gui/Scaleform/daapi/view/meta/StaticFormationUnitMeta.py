# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationUnitMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class StaticFormationUnitMeta(BaseRallyRoomView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseRallyRoomView
    null
    """

    def toggleStatusRequest(self):
        """
        :return :
        """
        self._printOverrideError('toggleStatusRequest')

    def setRankedMode(self, isRanked):
        """
        :param isRanked:
        :return :
        """
        self._printOverrideError('setRankedMode')

    def showTeamCard(self):
        """
        :return :
        """
        self._printOverrideError('showTeamCard')

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

    def as_setLegionnairesCountS(self, visible, legionnairesCount):
        """
        :param visible:
        :param legionnairesCount:
        :return :
        """
        return self.flashObject.as_setLegionnairesCount(visible, legionnairesCount) if self._isDAAPIInited() else None

    def as_setHeaderDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setHeaderData(data) if self._isDAAPIInited() else None

    def as_setTeamIconS(self, icon):
        """
        :param icon:
        :return :
        """
        return self.flashObject.as_setTeamIcon(icon) if self._isDAAPIInited() else None
