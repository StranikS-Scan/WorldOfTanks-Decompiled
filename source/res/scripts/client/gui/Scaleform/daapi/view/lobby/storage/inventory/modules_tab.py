# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/modules_tab.py
from gui.Scaleform.daapi.view.lobby.storage.inventory.inventory_view import FiltrableInventoryCategoryTabView
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.gui_items import GUI_ITEM_TYPE
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

class ModulesTabView(FiltrableInventoryCategoryTabView):
    filterItems = _TYPE_FILTER_ITEMS

    def _getClientSectionKey(self):
        pass

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.VEHICLE_MODULES

    def _getFilteredCriteria(self):
        criteria = REQ_CRITERIA.EMPTY
        typeIds = [ _TYPE_ID_BIT_TO_TYPE_ID_MAP[bit] for bit in _TYPE_ID_BIT_TO_TYPE_ID_MAP.iterkeys() if self._filterMask & bit ]
        if typeIds:
            criteria |= REQ_CRITERIA.ITEM_TYPES(*typeIds)
        if self._selectedVehicle:
            criteria |= REQ_CRITERIA.VEHICLE.SUITABLE([self._selectedVehicle])
        return criteria

    def _getRequestCriteria(self, invVehicles):
        criteria = REQ_CRITERIA.INVENTORY
        criteria |= REQ_CRITERIA.TYPE_CRITERIA(GUI_ITEM_TYPE.VEHICLE_MODULES, REQ_CRITERIA.VEHICLE.SUITABLE(invVehicles))
        return criteria
