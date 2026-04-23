# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inhangar/in_hangar_view.py
from collections import namedtuple
from gui.Scaleform.daapi.view.common.filter_popover import VehiclesFilterPopover
from gui.Scaleform.daapi.view.meta.StorageCategoryInHangarViewMeta import StorageCategoryInHangarViewMeta
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache
StorageCategoryInHangarDataVO = namedtuple('StorageCategoryInHangarDataVO', ('displayString', 'isZeroCount', 'shouldShow', 'searchInputLabel', 'searchInputName', 'searchInputTooltip', 'searchInputMaxChars'))
_SEARCH_INPUT_MAX_CHARS = 50
_TABS_DATA = ({'id': STORAGE_CONSTANTS.VEHICLES_TAB_ALL,
  'label': STORAGE.INHANGAR_TABS_ALL,
  'linkage': STORAGE_CONSTANTS.IN_HANGAR_ALL_VEHICLES_TAB,
  'selected': False}, {'id': STORAGE_CONSTANTS.VEHICLES_TAB_RESTORE,
  'label': STORAGE.INHANGAR_TABS_RESTORE,
  'linkage': STORAGE_CONSTANTS.IN_HANGAR_RESTORE_VEHICLES_TAB,
  'selected': False})
_RENT_TAB_DATA = {'id': STORAGE_CONSTANTS.VEHICLES_TAB_RENT,
 'label': STORAGE.INHANGAR_TABS_RENT,
 'linkage': STORAGE_CONSTANTS.IN_HANGAR_RENT_VEHICLES_TAB,
 'selected': False}

class StorageVehicleFilterPopover(VehiclesFilterPopover):

    def _getInitialVO(self, filters, xpRateMultiplier):
        vo = super(StorageVehicleFilterPopover, self)._getInitialVO(filters, xpRateMultiplier)
        vo['searchSectionVisible'] = False
        return vo


class StorageCategoryInHangarView(StorageCategoryInHangarViewMeta):
    _itemsCache = dependency.descriptor(IItemsCache)

    def setActiveState(self, isActive):
        self.setActive(isActive)

    def setActiveTab(self, tabId):
        tabsData = self.__getTabsData()
        defaultTabId = STORAGE_CONSTANTS.VEHICLES_TAB_ALL
        selectedId = tabId or defaultTabId
        defaultTab = None
        selectedFound = False
        for tab in tabsData:
            tab['selected'] = False
            tabIdValue = tab.get('id')
            if tabIdValue == defaultTabId:
                defaultTab = tab
            if tabIdValue == selectedId:
                tab['selected'] = True
                selectedFound = True

        if not selectedFound and defaultTab is not None:
            defaultTab['selected'] = True
        self.as_setTabsDataS(tabsData)
        return

    def _populate(self):
        super(StorageCategoryInHangarView, self)._populate()
        self.setActiveTab(STORAGE_CONSTANTS.VEHICLES_TAB_ALL)

    def __getTabsData(self):
        tabs = [ dict(tab) for tab in _TABS_DATA ]
        if self.__canShowRentTab():
            tabs.append(dict(_RENT_TAB_DATA))
        return tabs

    def __canShowRentTab(self):
        criteria = REQ_CRITERIA.VEHICLE.RENT
        criteria |= ~REQ_CRITERIA.VEHICLE.IS_STORAGE_HIDDEN
        criteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
        criteria |= ~REQ_CRITERIA.VEHICLE.WOT_PLUS_VEHICLE
        criteria |= ~REQ_CRITERIA.VEHICLE.HIDDEN_IN_HANGAR
        return bool(self._itemsCache.items.getItems(GUI_ITEM_TYPE.VEHICLE, criteria))
