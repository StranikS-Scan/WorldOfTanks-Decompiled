# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleListPopupMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class VehicleListPopupMeta(AbstractWindowView):

    def onSelectVehicles(self, item):
        self._printOverrideError('onSelectVehicles')

    def applyFilters(self, nation, vehicleType):
        self._printOverrideError('applyFilters')

    def as_setListDataS(self, listData, selectedItems):
        return self.flashObject.as_setListData(listData, selectedItems) if self._isDAAPIInited() else None

    def as_setInfoTextS(self, text):
        return self.flashObject.as_setInfoText(text) if self._isDAAPIInited() else None

    def as_setFiltersDataS(self, data):
        return self.flashObject.as_setFiltersData(data) if self._isDAAPIInited() else None
