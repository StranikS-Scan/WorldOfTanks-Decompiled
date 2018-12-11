# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_add_vehicle_popover.py
from gui.Scaleform.daapi.view.lobby.popover.vehicle_select_popover_base import VehicleSelectPopoverBase
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import packHeaderColumnData
from gui.Scaleform.daapi.view.lobby.vehicle_selector_base import VehicleSelectorBase
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.game_control.veh_comparison_basket import MAX_VEHICLES_TO_COMPARE_COUNT, getVehicleCriteriaForComparing
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import getSmallIconPath, getTypeSmallIconPath
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache

def _makeVehicleCmpVO(vehicle):
    return {'dbID': vehicle.intCD,
     'level': vehicle.level,
     'shortUserName': vehicle.shortUserName,
     'smallIconPath': getSmallIconPath(vehicle.name),
     'nationID': vehicle.nationID,
     'type': vehicle.type,
     'typeIcon': getTypeSmallIconPath(vehicle.type, vehicle.isPremium),
     'selected': False,
     'inHangar': vehicle.isInInventory}


class VehicleCompareAddVehiclePopover(VehicleSelectPopoverBase, VehicleSelectorBase):
    itemsCache = dependency.descriptor(IItemsCache)
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def initFilters(self):
        filters = self._initFilter(nation=-1, vehicleType='none', isMain=False, level=-1, compatibleOnly=False)
        self._updateFilter(filters['nation'], filters['vehicleType'], filters['isMain'], filters['level'], filters['compatibleOnly'])
        filters.update({'compatibleOnlyLabel': VEH_COMPARE.ADDVEHPOPOVER_SHOWONLYMYVAHICLES})
        return filters

    def applyFilters(self, nation, vehicleType, level, isMain, hangarOnly):
        self._updateFilter(nation, vehicleType, isMain, level, hangarOnly)
        self.updateData()

    def updateData(self, allVehicles=None):
        allVehicles = allVehicles or []
        if not allVehicles:
            allVehicles.append(self.itemsCache.items.getVehicles(getVehicleCriteriaForComparing()))
        vehicles = self._updateData(allVehicles[0], compatiblePredicate=lambda vo: vo['inHangar'])
        self._vehDP.buildList(vehicles)
        self._updateSortField()

    def setVehicleSelected(self, dbID, autoClose):
        super(VehicleCompareAddVehiclePopover, self).setVehicleSelected(dbID, autoClose)
        if not autoClose:
            self.updateAddButtonLabel()

    def updateAddButtonLabel(self):
        selectedCount = len(self._vehDP.getSelected())
        if self.comparisonBasket.getVehiclesCount() + selectedCount > MAX_VEHICLES_TO_COMPARE_COUNT:
            tooltip = VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_ADDTOCOMPAREDISABLED
            icon = RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON
            isEnabled = False
        else:
            tooltip = VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_ADDTOCOMPARE
            icon = None
            isEnabled = selectedCount > 0
        self.as_setAddButtonStateS({'btnLabel': _ms(VEH_COMPARE.ADDVEHPOPOVER_BTNADD, count=selectedCount),
         'btnTooltip': tooltip,
         'btnIcon': icon,
         'btnEnabled': isEnabled})
        return

    def addButtonClicked(self):
        vehicles = self._vehDP.getSelected()
        self.comparisonBasket.addVehicles(vehicles)
        self.onWindowClose()

    def _populate(self):
        super(VehicleCompareAddVehiclePopover, self)._populate()
        self.__initControls()
        self._initDP()
        self.comparisonBasket.onSwitchChange += self.__onVehCmpBasketStateChanged
        self.updateData()
        self.updateAddButtonLabel()

    def _dispose(self):
        self.comparisonBasket.onSwitchChange -= self.__onVehCmpBasketStateChanged
        super(VehicleCompareAddVehiclePopover, self)._dispose()

    def _makeVehicleVOAction(self, vehicle):
        return _makeVehicleCmpVO(vehicle)

    def __onVehCmpBasketStateChanged(self):
        if not self.comparisonBasket.isEnabled():
            self.onWindowClose()

    def __initControls(self):
        common = {'btnHeight': 34,
         'enabled': True}
        headers = [packHeaderColumnData('check', 45, icon=RES_ICONS.MAPS_ICONS_BUTTONS_ICON_TABLE_COMPARISON_CHECKMARK, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_SELECTVEHICLE, **common),
         packHeaderColumnData('nations', 45, icon=RES_ICONS.MAPS_ICONS_FILTERS_NATIONS_ALL, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_NATION, **common),
         packHeaderColumnData('type', 45, icon=RES_ICONS.MAPS_ICONS_FILTERS_TANKS_ALL, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_TYPE, **common),
         packHeaderColumnData('level', 45, icon=RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_LEVEL, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_LEVEL, **common),
         packHeaderColumnData('name', 130, label=VEH_COMPARE.ADDVEHPOPOVER_VEHICLENAME, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_TITLE, direction='ascending', **common),
         packHeaderColumnData('hangar', 45, icon=RES_ICONS.MAPS_ICONS_BUTTONS_ICON_TABLE_COMPARISON_INHANGAR, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_INHANGAR, **common)]
        self.as_setInitDataS({'tableHeaders': headers,
         'filters': self.initFilters(),
         'header': text_styles.highTitle(_ms(VEH_COMPARE.ADDVEHPOPOVER_HEADER)),
         'btnCancel': VEH_COMPARE.ADDVEHPOPOVER_BTNCANCEL})
