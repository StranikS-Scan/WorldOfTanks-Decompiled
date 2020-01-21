# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/consumables_tab.py
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import getBuyEquipmentUrl
from gui.Scaleform.daapi.view.meta.RegularItemsWithTypeFilterTabViewMeta import RegularItemsWithTypeFilterTabViewMeta
from gui.impl.gen import R
from gui.shared.event_dispatcher import showWebShop
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from shared_utils import CONST_CONTAINER

class _ConsumableFilterBit(CONST_CONTAINER):
    CONSUMABLES = 1
    BATTLE_BOOSTERS = 2
    DEMOUNT_KITS = 4


_TYPE_FILTER_ITEMS = [{'filterValue': _ConsumableFilterBit.CONSUMABLES,
  'selected': False,
  'tooltip': R.strings.storage.inventory.filterType.consumables,
  'icon': R.images.gui.maps.icons.storage.filters.icon_button_consumables}, {'filterValue': _ConsumableFilterBit.BATTLE_BOOSTERS,
  'selected': False,
  'tooltip': R.strings.storage.inventory.filterType.instructions,
  'icon': R.images.gui.maps.icons.storage.filters.icon_button_instructions}, {'filterValue': _ConsumableFilterBit.DEMOUNT_KITS,
  'selected': False,
  'tooltip': R.strings.storage.inventory.filterType.other,
  'icon': R.images.gui.maps.icons.storage.filters.icon_button_other}]
_TYPE_ID_BIT_TO_TYPE_ID_MAP = {_ConsumableFilterBit.CONSUMABLES: (GUI_ITEM_TYPE.EQUIPMENT,),
 _ConsumableFilterBit.BATTLE_BOOSTERS: (GUI_ITEM_TYPE.BATTLE_BOOSTER,),
 _ConsumableFilterBit.DEMOUNT_KITS: (GUI_ITEM_TYPE.DEMOUNT_KIT,)}

class ConsumablesTabView(RegularItemsWithTypeFilterTabViewMeta):
    filterItems = _TYPE_FILTER_ITEMS

    def navigateToStore(self):
        showWebShop(getBuyEquipmentUrl())

    def _getItemTypeID(self):
        return (GUI_ITEM_TYPE.EQUIPMENT, GUI_ITEM_TYPE.BATTLE_BOOSTER, GUI_ITEM_TYPE.DEMOUNT_KIT)

    def _getClientSectionKey(self):
        pass

    def _getFilteredCriteria(self):
        criteria = super(ConsumablesTabView, self)._getFilteredCriteria()
        typeIds = list()
        for bit in _TYPE_ID_BIT_TO_TYPE_ID_MAP.iterkeys():
            if self._filterMask & bit:
                typeIds.extend(_TYPE_ID_BIT_TO_TYPE_ID_MAP[bit])

        if typeIds:
            criteria |= REQ_CRITERIA.ITEM_TYPES(*set(typeIds))
        return criteria

    def _getRequestCriteria(self, invVehicles):
        criteria = REQ_CRITERIA.INVENTORY
        return criteria
