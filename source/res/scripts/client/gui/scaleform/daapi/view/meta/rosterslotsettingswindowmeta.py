# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RosterSlotSettingsWindowMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class RosterSlotSettingsWindowMeta(AbstractWindowView):

    def onFiltersUpdate(self, nation, vehicleType, isMain, level, compatibleOnly):
        self._printOverrideError('onFiltersUpdate')

    def requestVehicleFilters(self):
        self._printOverrideError('requestVehicleFilters')

    def submitButtonHandler(self, value):
        self._printOverrideError('submitButtonHandler')

    def cancelButtonHandler(self):
        self._printOverrideError('cancelButtonHandler')

    def as_setVehicleSelectionS(self, data):
        """
        :param data: Represented by VehicleVO (AS)
        """
        return self.flashObject.as_setVehicleSelection(data) if self._isDAAPIInited() else None

    def as_setRangeSelectionS(self, data):
        """
        :param data: Represented by SettingRosterVO (AS)
        """
        return self.flashObject.as_setRangeSelection(data) if self._isDAAPIInited() else None

    def as_resetSelectionS(self):
        return self.flashObject.as_resetSelection() if self._isDAAPIInited() else None

    def as_selectTabS(self, index):
        return self.flashObject.as_selectTab(index) if self._isDAAPIInited() else None

    def as_setListDataS(self, listData):
        """
        :param listData: Represented by DataProvider.<VehicleSelectorItemVO> (AS)
        """
        return self.flashObject.as_setListData(listData) if self._isDAAPIInited() else None

    def as_setStaticDataS(self, data):
        """
        :param data: Represented by RosterSlotSettingsWindowStaticVO (AS)
        """
        return self.flashObject.as_setStaticData(data) if self._isDAAPIInited() else None

    def as_setRosterLimitsS(self, data):
        """
        :param data: Represented by RosterLimitsVO (AS)
        """
        return self.flashObject.as_setRosterLimits(data) if self._isDAAPIInited() else None

    def as_updateVehicleFiltersS(self, data):
        """
        :param data: Represented by VehicleSelectorFilterVO (AS)
        """
        return self.flashObject.as_updateVehicleFilters(data) if self._isDAAPIInited() else None
