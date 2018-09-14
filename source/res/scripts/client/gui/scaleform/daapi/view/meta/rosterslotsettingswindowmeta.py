# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RosterSlotSettingsWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class RosterSlotSettingsWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def onFiltersUpdate(self, nation, vehicleType, isMain, level, compatibleOnly):
        """
        :param nation:
        :param vehicleType:
        :param isMain:
        :param level:
        :param compatibleOnly:
        :return :
        """
        self._printOverrideError('onFiltersUpdate')

    def requestVehicleFilters(self):
        """
        :return :
        """
        self._printOverrideError('requestVehicleFilters')

    def submitButtonHandler(self, value):
        """
        :param value:
        :return :
        """
        self._printOverrideError('submitButtonHandler')

    def cancelButtonHandler(self):
        """
        :return :
        """
        self._printOverrideError('cancelButtonHandler')

    def as_setVehicleSelectionS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setVehicleSelection(data) if self._isDAAPIInited() else None

    def as_setRangeSelectionS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setRangeSelection(data) if self._isDAAPIInited() else None

    def as_resetSelectionS(self):
        """
        :return :
        """
        return self.flashObject.as_resetSelection() if self._isDAAPIInited() else None

    def as_selectTabS(self, index):
        """
        :param index:
        :return :
        """
        return self.flashObject.as_selectTab(index) if self._isDAAPIInited() else None

    def as_setListDataS(self, listData):
        """
        :param listData:
        :return :
        """
        return self.flashObject.as_setListData(listData) if self._isDAAPIInited() else None

    def as_setStaticDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setStaticData(data) if self._isDAAPIInited() else None

    def as_setRosterLimitsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setRosterLimits(data) if self._isDAAPIInited() else None

    def as_updateVehicleFiltersS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateVehicleFilters(data) if self._isDAAPIInited() else None
