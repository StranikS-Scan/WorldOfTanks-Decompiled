# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/vehicle_view.py
from gui.Scaleform.daapi.view.lobby.storage.category_view import InventoryCategoryView
from gui.shared.gui_items import GUI_ITEM_TYPE

class VehicleView(InventoryCategoryView):

    def _populate(self):
        super(VehicleView, self)._populate()
        self._itemsCache.onSyncCompleted += self._onCacheResync

    def _dispose(self):
        self._itemsCache.onSyncCompleted -= self._onCacheResync
        super(VehicleView, self)._dispose()

    def _buildItems(self):
        pass

    def _getVO(self, item):
        pass

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.VEHICLE

    def _onCacheResync(self, *args):
        raise NotImplementedError
