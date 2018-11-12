# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/modules_tab.py
from gui.Scaleform.daapi.view.meta.ItemsWithVehicleFilterTabViewMeta import ItemsWithVehicleFilterTabViewMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.utils.functions import makeTooltip
from shared_utils import CONST_CONTAINER

class _ModuleFilterBit(CONST_CONTAINER):
    GUN = 1
    TURRET = 2
    ENGINE = 4
    CHASSIS = 8
    RADIO = 16


_TYPE_FILTER_ITEMS = [{'filterValue': _ModuleFilterBit.GUN,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_MODULES_BTNS_TYPE_GUNS),
  'icon': RES_ICONS.MAPS_ICONS_STORAGE_FILTERS_ICON_BUTTON_GUN},
 {'filterValue': _ModuleFilterBit.TURRET,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_MODULES_BTNS_TYPE_TOWERS),
  'icon': RES_ICONS.MAPS_ICONS_STORAGE_FILTERS_ICON_BUTTON_TURRET},
 {'filterValue': _ModuleFilterBit.ENGINE,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_MODULES_BTNS_TYPE_ENGINES),
  'icon': RES_ICONS.MAPS_ICONS_STORAGE_FILTERS_ICON_BUTTON_ENGINE},
 {'filterValue': _ModuleFilterBit.CHASSIS,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_MODULES_BTNS_TYPE_CHASSIS),
  'icon': RES_ICONS.MAPS_ICONS_STORAGE_FILTERS_ICON_BUTTON_TRUCK},
 {'filterValue': _ModuleFilterBit.RADIO,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_MODULES_BTNS_TYPE_RADIOS),
  'icon': RES_ICONS.MAPS_ICONS_STORAGE_FILTERS_ICON_BUTTON_RADIO}]
_TYPE_ID_BIT_TO_TYPE_ID_MAP = {_ModuleFilterBit.GUN: GUI_ITEM_TYPE.GUN,
 _ModuleFilterBit.TURRET: GUI_ITEM_TYPE.TURRET,
 _ModuleFilterBit.ENGINE: GUI_ITEM_TYPE.ENGINE,
 _ModuleFilterBit.CHASSIS: GUI_ITEM_TYPE.CHASSIS,
 _ModuleFilterBit.RADIO: GUI_ITEM_TYPE.RADIO}

class ModulesTabView(ItemsWithVehicleFilterTabViewMeta):

    def __init__(self):
        super(ModulesTabView, self).__init__()
        self.__isActive = False

    def setActiveState(self, isActive):
        super(ModulesTabView, self).setActiveState(isActive)
        self.__isActive = isActive

    def sellItem(self, itemId):
        self._sellItems(itemId)

    def _populate(self):
        super(ModulesTabView, self)._populate()
        self.__initFilter()
        self.addListener(events.StorageEvent.VEHICLE_SELECTED, self.__onVehicleSelected, scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.removeListener(events.StorageEvent.VEHICLE_SELECTED, self.__onVehicleSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        super(ModulesTabView, self)._dispose()

    def _getFilteredCriteria(self):
        criteria = REQ_CRITERIA.EMPTY
        typeIds = [ _TYPE_ID_BIT_TO_TYPE_ID_MAP[bit] for bit in _TYPE_ID_BIT_TO_TYPE_ID_MAP.iterkeys() if self._filterMask & bit ]
        if typeIds:
            criteria |= REQ_CRITERIA.ITEM_TYPES(*typeIds)
        if self._selectedVehicle:
            criteria |= REQ_CRITERIA.VEHICLE.SUITABLE([self._selectedVehicle])
        return criteria

    def onFiltersChange(self, filterMask):
        self._filterMask = filterMask
        self._buildItems()

    def resetFilter(self):
        self._filterMask = 0
        self._selectedVehicle = None
        self.as_updateVehicleFilterButtonS()
        self.as_resetFilterS(self._filterMask)
        self._buildItems()
        return

    def _buildItems(self):
        super(ModulesTabView, self)._buildItems()
        self.__updateUI()

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
        if event.ctx and event.ctx.get('vehicleId') and self.__isActive:
            self._selectedVehicle = vehicle = self.itemsCache.items.getItemByCD(event.ctx['vehicleId'])
            self.as_updateVehicleFilterButtonS(self._makeVehicleVO(vehicle))
            self._buildItems()
