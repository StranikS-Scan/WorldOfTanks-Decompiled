# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleSelectorPopupMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class VehicleSelectorPopupMeta(AbstractWindowView):

    def onFiltersUpdate(self, nation, vehicleType, isMain, level, compatibleOnly):
        self._printOverrideError('onFiltersUpdate')

    def onSelectVehicles(self, items):
        self._printOverrideError('onSelectVehicles')

    def as_setFiltersDataS(self, data):
        return self.flashObject.as_setFiltersData(data) if self._isDAAPIInited() else None

    def as_setListDataS(self, listData, selectedItems):
        return self.flashObject.as_setListData(listData, selectedItems) if self._isDAAPIInited() else None

    def as_setListModeS(self, isMultipleSelect):
        return self.flashObject.as_setListMode(isMultipleSelect) if self._isDAAPIInited() else None

    def as_setTextsS(self, titleText, infoText, selectButtonLabel, cancelButtonLabel):
        return self.flashObject.as_setTexts(titleText, infoText, selectButtonLabel, cancelButtonLabel) if self._isDAAPIInited() else None
