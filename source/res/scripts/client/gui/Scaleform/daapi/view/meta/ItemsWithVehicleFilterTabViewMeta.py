# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ItemsWithVehicleFilterTabViewMeta.py
from gui.Scaleform.daapi.view.lobby.storage.inventory.inventory_view import FiltrableInventoryCategoryTabView

class ItemsWithVehicleFilterTabViewMeta(FiltrableInventoryCategoryTabView):

    def sellItem(self, itemId):
        self._printOverrideError('sellItem')

    def resetFilter(self):
        self._printOverrideError('resetFilter')

    def onFiltersChange(self, filters):
        self._printOverrideError('onFiltersChange')

    def as_initFilterS(self, typeFiltersVO, vehicleFilterVO=None):
        return self.flashObject.as_initFilter(typeFiltersVO, vehicleFilterVO) if self._isDAAPIInited() else None

    def as_resetFilterS(self, resetData):
        return self.flashObject.as_resetFilter(resetData) if self._isDAAPIInited() else None

    def as_updateCounterS(self, shouldShow, displayString, isZeroCount):
        return self.flashObject.as_updateCounter(shouldShow, displayString, isZeroCount) if self._isDAAPIInited() else None

    def as_updateVehicleFilterButtonS(self, vehicleFilterVO=None):
        return self.flashObject.as_updateVehicleFilterButton(vehicleFilterVO) if self._isDAAPIInited() else None
