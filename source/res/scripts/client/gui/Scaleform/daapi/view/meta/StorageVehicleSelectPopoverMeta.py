# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StorageVehicleSelectPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class StorageVehicleSelectPopoverMeta(SmartPopOverView):

    def setVehicleSelected(self, intCD, autoClose):
        self._printOverrideError('setVehicleSelected')

    def applyFilters(self, nation, vehicleType, level, isMain):
        self._printOverrideError('applyFilters')

    def changeSearchNameVehicle(self, inputText):
        self._printOverrideError('changeSearchNameVehicle')

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_getTableDPS(self):
        return self.flashObject.as_getTableDP() if self._isDAAPIInited() else None

    def as_updateTableSortFieldS(self, sortField, sortDirection):
        return self.flashObject.as_updateTableSortField(sortField, sortDirection) if self._isDAAPIInited() else None

    def as_updateSearchS(self, searchInputLabel, searchInputName, searchInputTooltip, searchInputMaxChars):
        return self.flashObject.as_updateSearch(searchInputLabel, searchInputName, searchInputTooltip, searchInputMaxChars) if self._isDAAPIInited() else None

    def as_showDummyS(self, show):
        return self.flashObject.as_showDummy(show) if self._isDAAPIInited() else None
