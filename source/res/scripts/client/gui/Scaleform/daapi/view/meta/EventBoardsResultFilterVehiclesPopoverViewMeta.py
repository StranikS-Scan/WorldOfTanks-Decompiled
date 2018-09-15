# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBoardsResultFilterVehiclesPopoverViewMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class EventBoardsResultFilterVehiclesPopoverViewMeta(SmartPopOverView):

    def setVehicleSelected(self, dbID):
        self._printOverrideError('setVehicleSelected')

    def applyFilters(self, nation, vehicleType, level, isMain, hangarOnly):
        self._printOverrideError('applyFilters')

    def resetFilters(self):
        self._printOverrideError('resetFilters')

    def as_setInitDataS(self, data):
        """
        :param data: Represented by EventBoardTableFilterVehiclesVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_getTableDPS(self):
        return self.flashObject.as_getTableDP() if self._isDAAPIInited() else None

    def as_updateTableSortFieldS(self, sortField, sortDirection):
        return self.flashObject.as_updateTableSortField(sortField, sortDirection) if self._isDAAPIInited() else None
