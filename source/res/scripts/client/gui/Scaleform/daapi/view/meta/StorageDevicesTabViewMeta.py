# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StorageDevicesTabViewMeta.py
from gui.Scaleform.daapi.view.lobby.storage.inventory.filters.filter_by_vehicle import FiltrableInventoryCategoryByVehicleTabView

class StorageDevicesTabViewMeta(FiltrableInventoryCategoryByVehicleTabView):

    def onRestoreButtonClick(self):
        self._printOverrideError('onRestoreButtonClick')

    def as_initModulesFilterS(self, data):
        return self.flashObject.as_initModulesFilter(data) if self._isDAAPIInited() else None

    def as_setRestoreButtonDataS(self, data):
        return self.flashObject.as_setRestoreButtonData(data) if self._isDAAPIInited() else None

    def as_setBalanceValueS(self, value):
        return self.flashObject.as_setBalanceValue(value) if self._isDAAPIInited() else None
