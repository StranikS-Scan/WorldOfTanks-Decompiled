# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ItemsWithVehicleFilterTabViewMeta.py
from gui.Scaleform.daapi.view.lobby.storage.inventory.filters.filter_by_type import FiltrableInventoryCategoryByTypeTabView

class ItemsWithVehicleFilterTabViewMeta(FiltrableInventoryCategoryByTypeTabView):

    def resetVehicleFilter(self):
        self._printOverrideError('resetVehicleFilter')

    def as_initVehicleFilterS(self, vehicleFilterVO):
        return self.flashObject.as_initVehicleFilter(vehicleFilterVO) if self._isDAAPIInited() else None

    def as_updateVehicleFilterButtonS(self, vehicleFilterVO):
        return self.flashObject.as_updateVehicleFilterButton(vehicleFilterVO) if self._isDAAPIInited() else None
