# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/shells_tab.py
from constants import SHELL_TYPES
from gui.Scaleform.daapi.view.lobby.storage import storage_helpers
from gui.Scaleform.daapi.view.lobby.storage.inventory.inventory_view import FiltrableInventoryCategoryTabView
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from shared_utils import CONST_CONTAINER

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

class ShellsTabView(FiltrableInventoryCategoryTabView):
    filterItems = _TYPE_FILTER_ITEMS

    def _getClientSectionKey(self):
        pass

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.SHELL

    def _getFilteredCriteria(self):
        criteria = REQ_CRITERIA.EMPTY
        kindsList = [ _TYPE_ID_BIT_TO_TYPE_ID_MAP[bit] for bit in _TYPE_ID_BIT_TO_TYPE_ID_MAP.iterkeys() if self._filterMask & bit ]
        if kindsList:
            criteria |= REQ_CRITERIA.SHELL.TYPE(kindsList)
        if self._selectedVehicle:
            criteria |= storage_helpers.getStorageShellsCriteria(self._itemsCache, [self._selectedVehicle], True)
        return criteria

    def _getRequestCriteria(self, invVehicles):
        criteria = REQ_CRITERIA.INVENTORY
        criteria |= REQ_CRITERIA.TYPE_CRITERIA((GUI_ITEM_TYPE.SHELL,), storage_helpers.getStorageShellsCriteria(self._itemsCache, invVehicles, True))
        return criteria
