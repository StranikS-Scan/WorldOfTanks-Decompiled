# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleSelectorPopupMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class VehicleSelectorPopupMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def onFiltersUpdate(self, nation, vehicleType, isMain, level, compatibleOnly):
        self._printOverrideError('onFiltersUpdate')

    def onSelectVehicles(self, items):
        self._printOverrideError('onSelectVehicles')

    def as_setFiltersDataS(self, data):
        """
        :param data: Represented by VehicleSelectorFilterVO (AS)
        """
        return self.flashObject.as_setFiltersData(data) if self._isDAAPIInited() else None

    def as_setListDataS(self, listData, selectedItems):
        """
        :param listData: Represented by DataProvider (AS)
        :param selectedItems: Represented by Array (AS)
        """
        return self.flashObject.as_setListData(listData, selectedItems) if self._isDAAPIInited() else None

    def as_setListModeS(self, isMultipleSelect):
        return self.flashObject.as_setListMode(isMultipleSelect) if self._isDAAPIInited() else None

    def as_setInfoTextS(self, text, componentsOffset):
        return self.flashObject.as_setInfoText(text, componentsOffset) if self._isDAAPIInited() else None
