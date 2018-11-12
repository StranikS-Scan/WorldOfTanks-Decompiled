# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/shells_tab.py
from gui.Scaleform.daapi.view.meta.ItemsWithVehicleFilterTabViewMeta import ItemsWithVehicleFilterTabViewMeta
from gui.Scaleform.daapi.view.lobby.storage import storage_helpers
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from shared_utils import CONST_CONTAINER
from constants import SHELL_TYPES

class _ShellsFilterBit(CONST_CONTAINER):
    ARMOR_PIERCING = 1
    ARMOR_PIERCING_GR = 2
    HOLLOW_CHARGE = 4
    HIGH_EXPLOSIVE = 8


_TYPE_FILTER_ITEMS = [{'filterValue': _ShellsFilterBit.ARMOR_PIERCING,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_SHELLS_BTNS_TYPE_ARMOR_PIERCING),
  'icon': RES_ICONS.MAPS_ICONS_STORAGE_FILTERS_ICON_ARMOR_PIERCING_GR},
 {'filterValue': _ShellsFilterBit.ARMOR_PIERCING_GR,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_SHELLS_BTNS_TYPE_ARMOR_PIERCING_CR),
  'icon': RES_ICONS.MAPS_ICONS_STORAGE_FILTERS_ICON_ARMOR_PIERCING_CR},
 {'filterValue': _ShellsFilterBit.HOLLOW_CHARGE,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_SHELLS_BTNS_TYPE_HOLLOW_CHARGE),
  'icon': RES_ICONS.MAPS_ICONS_STORAGE_FILTERS_ICON_HOLLOW_CHARGE},
 {'filterValue': _ShellsFilterBit.HIGH_EXPLOSIVE,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_SHELLS_BTNS_TYPE_HIGH_EXPLOSIVE),
  'icon': RES_ICONS.MAPS_ICONS_STORAGE_FILTERS_ICON_HIGH_EXPLOSIVE}]
_TYPE_ID_BIT_TO_TYPE_ID_MAP = {_ShellsFilterBit.ARMOR_PIERCING: SHELL_TYPES.ARMOR_PIERCING,
 _ShellsFilterBit.ARMOR_PIERCING_GR: SHELL_TYPES.ARMOR_PIERCING_CR,
 _ShellsFilterBit.HOLLOW_CHARGE: SHELL_TYPES.HOLLOW_CHARGE,
 _ShellsFilterBit.HIGH_EXPLOSIVE: SHELL_TYPES.HIGH_EXPLOSIVE}

class ShellsTabView(ItemsWithVehicleFilterTabViewMeta):

    def __init__(self):
        super(ShellsTabView, self).__init__()
        self.__isActive = False

    def setActiveState(self, isActive):
        super(ShellsTabView, self).setActiveState(isActive)
        self.__isActive = isActive

    def _populate(self):
        super(ShellsTabView, self)._populate()
        self.__initFilter()
        self.addListener(events.StorageEvent.VEHICLE_SELECTED, self.__onVehicleSelected, scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.removeListener(events.StorageEvent.VEHICLE_SELECTED, self.__onVehicleSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        super(ShellsTabView, self)._dispose()

    def sellItem(self, itemId):
        self._sellItems(itemId)

    def onFiltersChange(self, filterMask):
        self._filterMask = filterMask
        self._buildItems()

    def _buildItems(self):
        super(ShellsTabView, self)._buildItems()
        self.__updateUI()

    def _getFilteredCriteria(self):
        criteria = REQ_CRITERIA.EMPTY
        kindsList = [ _TYPE_ID_BIT_TO_TYPE_ID_MAP[bit] for bit in _TYPE_ID_BIT_TO_TYPE_ID_MAP.iterkeys() if self._filterMask & bit ]
        if kindsList:
            criteria |= REQ_CRITERIA.SHELL.TYPE(kindsList)
        if self._selectedVehicle:
            criteria |= storage_helpers.getStorageShellsCriteria(self.itemsCache, [self._selectedVehicle], True)
        return criteria

    def resetFilter(self):
        self._filterMask = 0
        self._selectedVehicle = None
        self.as_updateVehicleFilterButtonS()
        self.as_resetFilterS(self._filterMask)
        self._buildItems()
        return

    def __updateUI(self):
        self.__updateFilterCounter()
        self.__updateScreen()

    def __initFilter(self):
        typeFilters = {'items': _TYPE_FILTER_ITEMS,
         'minSelectedItems': 0}
        self.as_initFilterS(typeFilters, self._makeVehicleVO(self._selectedVehicle))

    def __updateFilterCounter(self):
        if self._totalCount != -1 and self._currentCount != -1:
            shouldShow = self._filterMask != 0 or bool(self._selectedVehicle)
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
            filterWarningVO = self._makeFilterWarningVO(STORAGE.FILTER_WARNINGMESSAGE, STORAGE.FILTER_NORESULTSBTN_LABEL, TOOLTIPS.STORAGE_FILTER_NORESULTSBTN)
        elif hasNoItems:
            self.as_showDummyScreenS(hasNoItems)
        self.as_showFilterWarningS(filterWarningVO)
        return

    def __onVehicleSelected(self, event):
        if event.ctx and self.__isActive:
            self._selectedVehicle = vehicle = self.itemsCache.items.getItemByCD(event.ctx['vehicleId'])
            self.as_updateVehicleFilterButtonS(self._makeVehicleVO(vehicle))
            self._buildItems()
