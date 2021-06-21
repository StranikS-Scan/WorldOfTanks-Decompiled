# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/opt_devices_tab.py
from enum import IntEnum
from gui.Scaleform.daapi.view.lobby.storage.inventory.filters.filter_by_vehicle import FiltrableInventoryCategoryByVehicleTabView
from gui.Scaleform.daapi.view.lobby.storage.inventory.inventory_view import TABS_SORT_ORDER, IN_GROUP_COMPARATOR
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyOptionalDevicesUrl
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.event_dispatcher import showShop
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from items.components.supply_slot_categories import SlotCategories

class _OptDeviceCategoriesFilterBit(IntEnum):
    FIREPOWER = 1
    SURVIVABILITY = 2
    MOBILITY = 4
    STEALTH = 8


_TYPE_FILTER_ITEMS = [{'filterValue': int(_OptDeviceCategoriesFilterBit.FIREPOWER),
  'selected': False,
  'tooltip': makeTooltip(header=backport.text(R.strings.tank_setup.categories.firepower()), body=backport.text(R.strings.tank_setup.categories.body.firepower())),
  'icon': backport.image(R.images.gui.maps.icons.specialization.firepower_filter())},
 {'filterValue': int(_OptDeviceCategoriesFilterBit.SURVIVABILITY),
  'selected': False,
  'tooltip': makeTooltip(header=backport.text(R.strings.tank_setup.categories.survivability()), body=backport.text(R.strings.tank_setup.categories.body.survivability())),
  'icon': backport.image(R.images.gui.maps.icons.specialization.survivability_filter())},
 {'filterValue': int(_OptDeviceCategoriesFilterBit.MOBILITY),
  'selected': False,
  'tooltip': makeTooltip(header=backport.text(R.strings.tank_setup.categories.mobility()), body=backport.text(R.strings.tank_setup.categories.body.mobility())),
  'icon': backport.image(R.images.gui.maps.icons.specialization.mobility_filter())},
 {'filterValue': int(_OptDeviceCategoriesFilterBit.STEALTH),
  'selected': False,
  'tooltip': makeTooltip(header=backport.text(R.strings.tank_setup.categories.stealth()), body=backport.text(R.strings.tank_setup.categories.body.stealth())),
  'icon': backport.image(R.images.gui.maps.icons.specialization.stealth_filter())}]
_BIT_TO_CATEGORIES_MAP = {_OptDeviceCategoriesFilterBit.FIREPOWER: SlotCategories.FIREPOWER,
 _OptDeviceCategoriesFilterBit.SURVIVABILITY: SlotCategories.SURVIVABILITY,
 _OptDeviceCategoriesFilterBit.MOBILITY: SlotCategories.MOBILITY,
 _OptDeviceCategoriesFilterBit.STEALTH: SlotCategories.STEALTH}

class OptDevicesTabView(FiltrableInventoryCategoryByVehicleTabView):
    filterItems = _TYPE_FILTER_ITEMS

    def _getTypeFilters(self, items):
        return {'items': items,
         'minSelectedItems': 0,
         'filterTypeName': backport.text(R.strings.storage.storage.tabs.devices.filter.type.label())}

    def navigateToStore(self):
        showShop(getBuyOptionalDevicesUrl())

    def upgradeItem(self, itemId):
        optDevice = self._itemsCache.items.getItemByCD(int(itemId))
        ItemsActionsFactory.doAction(ItemsActionsFactory.UPGRADE_OPT_DEVICE, optDevice, None, None)
        return

    def _getClientSectionKey(self):
        pass

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.OPTIONALDEVICE

    def _getFilteredCriteria(self):
        criteria = super(OptDevicesTabView, self)._getFilteredCriteria()
        categories = [ _BIT_TO_CATEGORIES_MAP[bit] for bit in _BIT_TO_CATEGORIES_MAP.iterkeys() if self._filterMask & bit ]
        if categories:
            criteria |= REQ_CRITERIA.OPTIONAL_DEVICE.SIMPLE
            criteria |= REQ_CRITERIA.OPTIONAL_DEVICE.HAS_ANY_FROM_CATEGORIES(*categories)
        if self._selectedVehicle:
            if not self._selectedVehicle.optDevices.layout.getCapacity():
                criteria |= REQ_CRITERIA.NONE
            else:
                criteria |= REQ_CRITERIA.VEHICLE.SUITABLE([self._selectedVehicle], self._getItemTypeIDs())
        return criteria

    def _getRequestCriteria(self, invVehicles):
        return REQ_CRITERIA.INVENTORY

    def _getComparator(self):

        def _comparator(a, b):
            return cmp(TABS_SORT_ORDER[a.itemTypeID], TABS_SORT_ORDER[b.itemTypeID]) or IN_GROUP_COMPARATOR[a.itemTypeID](a, b)

        return _comparator

    def _buildItems(self):
        super(OptDevicesTabView, self)._buildItems()
        self.as_showDummyScreenS(not self._dataProvider.collection)
