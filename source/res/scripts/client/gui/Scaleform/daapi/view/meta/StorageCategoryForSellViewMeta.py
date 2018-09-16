# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StorageCategoryForSellViewMeta.py
from gui.Scaleform.daapi.view.lobby.storage.category_view import InventoryCategoryView

class StorageCategoryForSellViewMeta(InventoryCategoryView):

    def navigateToStore(self):
        self._printOverrideError('navigateToStore')

    def selectItem(self, itemId, isSelected):
        self._printOverrideError('selectItem')

    def selectAll(self, isSelected):
        self._printOverrideError('selectAll')

    def sellItem(self, itemId):
        self._printOverrideError('sellItem')

    def sellAll(self):
        self._printOverrideError('sellAll')

    def as_initS(self, data):
        return self.flashObject.as_init(data) if self._isDAAPIInited() else None
