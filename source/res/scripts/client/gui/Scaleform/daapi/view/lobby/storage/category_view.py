# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/category_view.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.storage import storage_helpers
from gui.Scaleform.daapi.view.meta.BaseStorageCategoryViewMeta import BaseStorageCategoryViewMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider
from gui.shared.formatters import text_styles
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class StorageDataProvider(DAAPIDataProvider):

    def __init__(self):
        super(StorageDataProvider, self).__init__()
        self._list = []

    @property
    def collection(self):
        return self._list

    def emptyItem(self):
        return {}

    def buildList(self, itemsVoList):
        if itemsVoList != self._list:
            self._list = itemsVoList
            self.refresh()

    def fini(self):
        self._list = None
        return


class BaseCategoryView(BaseStorageCategoryViewMeta):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(BaseCategoryView, self).__init__()
        self._dataProvider = self._createDataProvider()

    def setActiveState(self, isActive):
        self.setActive(isActive)
        if isActive:
            self._update()

    def playInfoSound(self):
        self.__playSound('shop_info')

    def _populate(self):
        super(BaseCategoryView, self)._populate()
        self._dataProvider.setFlashObject(self.as_getCardsDPS())

    def _dispose(self):
        super(BaseCategoryView, self)._dispose()
        self._dataProvider.fini()
        self._dataProvider = None
        return

    def _createDataProvider(self):
        return StorageDataProvider()

    def _update(self, *args):
        pass

    def __playSound(self, soundName):
        if self.app is not None and self.app.soundManager is not None:
            self.app.soundManager.playEffectSound(soundName)
        return

    def _makeFilterWarningVO(self, label, btnLabel, btnTooltip):
        return storage_helpers.dummyFormatter(label, btnLabel=btnLabel, btnTooltip=btnTooltip)

    def _formatCountString(self, currentItemsCount, totalItemsCount):
        style = text_styles.error if currentItemsCount == 0 else text_styles.stats
        return '{} / {}'.format(style(currentItemsCount), text_styles.main(totalItemsCount))

    def _formatTotalCountString(self, totalItemsCount):
        return text_styles.stats(totalItemsCount)


class InventoryCategoryView(BaseCategoryView):

    def __init__(self):
        super(InventoryCategoryView, self).__init__()
        self._invVehicles = None
        return

    def _populate(self):
        super(InventoryCategoryView, self)._populate()
        self._invVehicles = self._itemsCache.items.getVehicles(self._getInvVehicleCriteria()).values()
        g_clientUpdateManager.addCallbacks({'inventory': self._inventoryUpdatesCallback})

    def _dispose(self):
        super(InventoryCategoryView, self)._dispose()
        self._invVehicles = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        return

    def _getRequestCriteria(self, invVehicles):
        return REQ_CRITERIA.EMPTY

    def _getInvVehicleCriteria(self):
        return REQ_CRITERIA.INVENTORY

    def _getComparator(self):
        return None

    def _getItemTypeID(self):
        raise NotImplementedError

    def _buildItems(self):
        self._dataProvider.buildList(self._getVoList())

    def _getVoList(self):
        criteria = self._getRequestCriteria(self._invVehicles)
        items = self._itemsCache.items.getItems(self._getItemTypeID(), criteria, nationID=None)
        dataProviderValues = []
        for item in sorted(items.itervalues(), cmp=self._getComparator()):
            dataProviderValues.append(self._getVO(item))

        return dataProviderValues

    def _getVO(self, item):
        raise NotImplementedError

    def _inventoryUpdatesCallback(self, *args):
        self._invVehicles = self._itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
        self._buildItems()

    def _update(self, *args):
        self._buildItems()
