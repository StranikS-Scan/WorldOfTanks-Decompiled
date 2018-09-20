# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inhangar/in_hangar_view.py
import copy
from collections import namedtuple
from gui.Scaleform.daapi.view.common.filter_popover import VehiclesFilterPopover
from gui.Scaleform.daapi.view.meta.StorageCategoryInHangarViewMeta import StorageCategoryInHangarViewMeta
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.locale.STORAGE import STORAGE
StorageCategoryInHangarDataVO = namedtuple('StorageCategoryInHangarDataVO', ('displayString', 'isZeroCount', 'shouldShow', 'searchInputLabel', 'searchInputName', 'searchInputTooltip', 'searchInputMaxChars'))
_SEARCH_INPUT_MAX_CHARS = 50
_TABS_DATA = ({'id': STORAGE_CONSTANTS.VEHICLES_TAB_ALL,
  'label': STORAGE.INHANGAR_TABS_ALL,
  'linkage': STORAGE_CONSTANTS.IN_HANGAR_ALL_VEHICLES_TAB,
  'selected': False}, {'id': STORAGE_CONSTANTS.VEHICLES_TAB_RESTORE,
  'label': STORAGE.INHANGAR_TABS_RESTORE,
  'linkage': STORAGE_CONSTANTS.IN_HANGAR_RESTORE_VEHICLES_TAB,
  'selected': False})

class StorageVehicleFilterPopover(VehiclesFilterPopover):

    def _getInitialVO(self, filters, xpRateMultiplier):
        vo = super(StorageVehicleFilterPopover, self)._getInitialVO(filters, xpRateMultiplier)
        vo['searchSectionVisible'] = False
        return vo


class StorageCategoryInHangarView(StorageCategoryInHangarViewMeta):

    def setActiveTab(self, tabId):
        activeIdx = 0
        for i, tab in enumerate(_TABS_DATA):
            if tab['id'] == tabId:
                activeIdx = i
                break

        tabsData = copy.deepcopy(_TABS_DATA)
        tabsData[activeIdx]['selected'] = True
        self.as_setTabsDataS(tabsData)

    def _populate(self):
        super(StorageCategoryInHangarView, self)._populate()
        self.setActiveTab(STORAGE_CONSTANTS.VEHICLES_TAB_ALL)
