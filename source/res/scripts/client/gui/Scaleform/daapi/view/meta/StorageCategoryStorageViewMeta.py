# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StorageCategoryStorageViewMeta.py
from gui.Scaleform.daapi.view.lobby.storage.category_view import InventoryCategoryView

class StorageCategoryStorageViewMeta(InventoryCategoryView):

    def navigateToStore(self):
        self._printOverrideError('navigateToStore')

    def sellItem(self, itemId):
        self._printOverrideError('sellItem')

    def showItemInfo(self, itemId):
        self._printOverrideError('showItemInfo')

    def onOpenTab(self, index):
        self._printOverrideError('onOpenTab')

    def as_setTabsDataS(self, tabs):
        return self.flashObject.as_setTabsData(tabs) if self._isDAAPIInited() else None
