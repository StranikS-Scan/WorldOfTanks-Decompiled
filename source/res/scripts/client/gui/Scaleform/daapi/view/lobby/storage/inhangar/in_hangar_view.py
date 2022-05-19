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
        if tabId:
            for i, tab in enumerate(tabsData):
                tabsData[i]['selected'] = False
                if tab.get('id') == tabId:
                    tabsData[i]['selected'] = True

        self.as_setTabsDataS(tabsData)

    def _populate(self):
        super(StorageCategoryInHangarView, self)._populate()
        self.setActiveTab(STORAGE_CONSTANTS.VEHICLES_TAB_ALL)

    def __getTabsData(self):
        return _TABS_DATA + (_RENT_TAB_DATA,) if self.__canShowRentTab() else _TABS_DATA

    def __canShowRentTab(self):
        criteria = REQ_CRITERIA.VEHICLE.RENT | ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
        return bool(self._itemsCache.items.getItems(GUI_ITEM_TYPE.VEHICLE, criteria))
