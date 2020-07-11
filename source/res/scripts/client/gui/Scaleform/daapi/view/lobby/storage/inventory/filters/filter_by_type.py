# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/filters/filter_by_type.py
import copy
import typing
from account_helpers import AccountSettings
from adisp import process
from gui import DialogsInterface
from gui import GUI_NATIONS_ORDER_INDICES
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import SellModuleMeta
from gui.Scaleform.daapi.view.lobby.storage import storage_helpers
from gui.Scaleform.daapi.view.lobby.storage.inventory.inventory_view import IN_GROUP_COMPARATOR
from gui.Scaleform.daapi.view.lobby.storage.inventory.inventory_view import TABS_SORT_ORDER
from gui.Scaleform.daapi.view.meta.ItemsWithTypeFilterTabViewMeta import ItemsWithTypeFilterTabViewMeta
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen_utils import DynAccessor
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
if typing.TYPE_CHECKING:
    from typing import Dict, Union, Callable

def processFilterEntry(item, field, calculator):
    entry = item.get(field, '')
    if isinstance(entry, DynAccessor):
        item[field] = calculator(entry)


class FiltrableInventoryCategoryByTypeTabView(ItemsWithTypeFilterTabViewMeta):
    filterItems = None

    def __init__(self):
        super(FiltrableInventoryCategoryByTypeTabView, self).__init__()
        self._filterMask = 0
        self._totalCount = -1
        self._currentCount = -1
        self.__loadFilters()

    def setActiveState(self, isActive):
        self.setActive(isActive)

    @process
    def sellItem(self, itemId):
        yield DialogsInterface.showDialog(SellModuleMeta(int(itemId)))

    def onFiltersChange(self, filterMask):
        self._filterMask = filterMask
        self._buildItems()

    def resetFilter(self):
        self._filterMask = 0
        self.as_resetFilterS(self._filterMask)
        self._buildItems()

    def _parseLoadedFilters(self, filterDict):
        self._filterMask = filterDict['filterMask']

    def _prepareDataForFilterSaving(self):
        return {'filterMask': self._filterMask}

    def _getClientSectionKey(self):
        raise NotImplementedError

    def _getFilteredCriteria(self):
        return REQ_CRITERIA.EMPTY

    def _initFilter(self):
        items = self._getInitFilterItems()
        for item in items:
            processFilterEntry(item, 'tooltip', lambda da: makeTooltip(body=backport.text(da())))
            processFilterEntry(item, 'icon', lambda da: backport.image(da()))
            if self._filterMask & item['filterValue'] == item['filterValue']:
                item.update({'selected': True})

        typeFilters = {'items': items,
         'minSelectedItems': 0}
        self.as_initTypeFilterS(typeFilters)

    def _populate(self):
        super(FiltrableInventoryCategoryByTypeTabView, self)._populate()
        self._initFilter()
        self._itemsCache.onSyncCompleted += self.__onCacheResync
        self._buildItems()

    def _dispose(self):
        self.__saveFilters()
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        super(FiltrableInventoryCategoryByTypeTabView, self)._dispose()

    def _buildItems(self):
        super(FiltrableInventoryCategoryByTypeTabView, self)._buildItems()
        self.__updateUI()

    def _getVO(self, item):
        return storage_helpers.getItemVo(item)

    def _getVoList(self):
        totalItems = self._getItemList()
        self._totalCount = len(totalItems.values())
        filterCriteria = self._getFilteredCriteria()
        dataProviderListVoItems = []
        for item in sorted(totalItems.itervalues(), cmp=self._getComparator()):
            if filterCriteria(item):
                dataProviderListVoItems.append(self._getVO(item))

        self._currentCount = sum((item['count'] for item in dataProviderListVoItems))
        return dataProviderListVoItems

    def containItemType(self, itemType):
        values = filter(self._getFilteredCriteria(), self._getItemList().values())
        return next((item for item in values if item.itemTypeID == itemType), None) is not None

    def _getComparator(self):

        def _comparator(a, b):
            return cmp(TABS_SORT_ORDER[a.itemTypeID], TABS_SORT_ORDER[b.itemTypeID]) or cmp(GUI_NATIONS_ORDER_INDICES[a.nationID], GUI_NATIONS_ORDER_INDICES[b.nationID]) or IN_GROUP_COMPARATOR[a.itemTypeID](a, b)

        return _comparator

    def _getInitFilterItems(self):
        return copy.deepcopy(self.filterItems) if self.filterItems is not None else []

    def _shouldShowCounter(self):
        return self._filterMask != 0

    def __loadFilters(self):
        if storage_helpers.isStorageSessionTimeout():
            return
        self._parseLoadedFilters(AccountSettings.getSessionSettings(self._getClientSectionKey()))

    def __saveFilters(self):
        AccountSettings.setSessionSettings(self._getClientSectionKey(), self._prepareDataForFilterSaving())

    def __updateUI(self):
        self.__updateFilterCounter()
        self.__updateScreen()

    def __updateFilterCounter(self):
        if self._totalCount != -1 and self._currentCount != -1:
            shouldShow = self._shouldShowCounter()
            if shouldShow:
                countString = self._formatCountString(self._currentCount, self._totalCount)
            else:
                countString = self._formatTotalCountString(self._totalCount)
            self.as_updateCounterS(shouldShow, countString, self._currentCount == 0)

    def __updateScreen(self):
        hasNoItems = self._totalCount == 0
        hasNoFilterResults = not hasNoItems and self._currentCount == 0
        filterWarningVO = None
        if hasNoFilterResults:
            filterWarningVO = self._makeFilterWarningVO(backport.text(R.strings.storage.filter.warningMessage()), backport.text(R.strings.storage.filter.noResultsBtn.label()), backport.text(R.strings.tooltips.storage.filter.noResultsBtn()))
        self.as_showDummyScreenS(hasNoItems)
        self.as_showFilterWarningS(filterWarningVO)
        return

    def __onCacheResync(self, *args):
        self._buildItems()


class FiltrableRegularCategoryByTypeTabView(FiltrableInventoryCategoryByTypeTabView):

    def _getItemList(self):
        criteria = self._getRequestCriteria(self._invVehicles)
        items = {}
        for itemType in self._getItemTypeIDs():
            if itemType == GUI_ITEM_TYPE.DEMOUNT_KIT:
                items.update(self._goodiesCache.getDemountKits(REQ_CRITERIA.DEMOUNT_KIT.IN_ACCOUNT | REQ_CRITERIA.DEMOUNT_KIT.IS_ENABLED))
            items.update(self._itemsCache.items.getItems(itemType, criteria, nationID=None))

        return items
