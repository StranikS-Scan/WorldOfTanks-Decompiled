# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleSelectPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class VehicleSelectPopoverMeta(SmartPopOverView):

    def setVehicleSelected(self, dbID):
        self._printOverrideError('setVehicleSelected')

    def applyFilters(self, nation, vehicleType, level, isMain, hangarOnly):
        self._printOverrideError('applyFilters')

    def addButtonClicked(self):
        self._printOverrideError('addButtonClicked')

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_getTableDPS(self):
        return self.flashObject.as_getTableDP() if self._isDAAPIInited() else None

    def as_setAddButtonStateS(self, data):
        return self.flashObject.as_setAddButtonState(data) if self._isDAAPIInited() else None

    def as_updateTableSortFieldS(self, sortField, sortDirection):
        return self.flashObject.as_updateTableSortField(sortField, sortDirection) if self._isDAAPIInited() else None
