# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_add_vehicle_popover.py
import nations
from gui import GUI_NATIONS_ORDER_INDEX_REVERSED
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import packHeaderColumnData
from gui.Scaleform.daapi.view.lobby.vehicle_selector_base import VehicleSelectorBase
from gui.Scaleform.daapi.view.meta.VehicleCompareAddVehiclePopoverMeta import VehicleCompareAddVehiclePopoverMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.game_control.veh_comparison_basket import MAX_VEHICLES_TO_COMPARE_COUNT, getVehicleCriteriaForComparing
from gui.shared import g_itemsCache
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import getSmallIconPath, VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED
from gui.shared.utils import sortByFields
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IVehicleComparisonBasket

def _makeVehicleCmpVO(vehicle):
    return {'dbID': vehicle.intCD,
     'level': vehicle.level,
     'shortUserName': vehicle.shortUserName,
     'smallIconPath': getSmallIconPath(vehicle.name),
     'nationID': vehicle.nationID,
     'type': vehicle.type,
     'selected': False,
     'inHangar': vehicle.isInInventory}


class VehicleCompareAddVehiclePopover(VehicleCompareAddVehiclePopoverMeta, VehicleSelectorBase):
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self, ctx=None):
        super(VehicleCompareAddVehiclePopover, self).__init__(ctx)
        self._vehDP = None
        return

    def initFilters(self):
        filters = self._initFilter(nation=-1, vehicleType='none', isMain=False, level=-1, compatibleOnly=False)
        self._updateFilter(filters['nation'], filters['vehicleType'], filters['isMain'], filters['level'], filters['compatibleOnly'])
        return filters

    def applyFilters(self, nation, vehicleType, level, isMain, hangarOnly):
        self._updateFilter(nation, vehicleType, isMain, level, hangarOnly)
        self.updateData()

    def updateData(self, allVehicles=[]):
        if not allVehicles:
            allVehicles.append(g_itemsCache.items.getVehicles(getVehicleCriteriaForComparing()))
        vehicles = self._updateData(allVehicles[0], compatiblePredicate=lambda vo: vo['inHangar'])
        self._vehDP.buildList(vehicles)
        self.__updateSortField()

    def setVehicleSelected(self, dbID):
        self._vehDP.toggleSelectionByID(dbID)
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
        assert vehicles
        self.comparisonBasket.addVehicles(vehicles)
        self.onWindowClose()

    def onWindowClose(self):
        self.destroy()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(VehicleCompareAddVehiclePopover, self)._onRegisterFlashComponent(viewPy, alias)

    def _populate(self):
        super(VehicleCompareAddVehiclePopover, self)._populate()
        self.__initControls()
        self._vehDP = VehiclesDataProvider()
        self._vehDP.setFlashObject(self.as_getTableDPS())
        self.comparisonBasket.onSwitchChange += self.onWindowClose
        self.updateData()
        self.updateAddButtonLabel()

    def _dispose(self):
        self.comparisonBasket.onSwitchChange -= self.onWindowClose
        super(VehicleCompareAddVehiclePopover, self)._dispose()
        self._vehDP.fini()
        self._vehDP = None
        return

    def _makeVehicleVOAction(self, vehicle):
        return _makeVehicleCmpVO(vehicle)

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

    def __updateSortField(self):
        sort = self._vehDP.getLastSortMethod()
        assert sort
        order = 'ascending' if sort[0][1] else 'descending'
        self.as_updateTableSortFieldS(sortField=sort[0][0], sortDirection=order)


class VehiclesDataProvider(SortableDAAPIDataProvider):

    def __init__(self):
        super(VehiclesDataProvider, self).__init__()
        self.__list = None
        self.__listMapping = {}
        self._sort = (('level', False),)
        self.__sortMapping = {'check': lambda v: v['selected'],
         'nations': lambda v: GUI_NATIONS_ORDER_INDEX_REVERSED[nations.NAMES[v['nationID']]],
         'type': lambda v: VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED[v['type']],
         'level': lambda v: v['level'] << 16 | GUI_NATIONS_ORDER_INDEX_REVERSED[nations.NAMES[v['nationID']]] << 8 | VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED[v['type']],
         'name': lambda v: v['shortUserName'],
         'hangar': lambda v: v['inHangar']}
        return

    @property
    def sortedCollection(self):
        return sortByFields(self._sort, self.__list, self.__sortingMethod)

    @property
    def collection(self):
        return self.__list

    def emptyItem(self):
        return None

    def pySortOn(self, fields, order):
        super(VehiclesDataProvider, self).pySortOn(fields, order)
        if self.__list:
            self.__list = sortByFields(self._sort, self.__list, self.__sortingMethod)
            self.buildList(self.__list)

    def buildList(self, vehicleVOs):
        self.__list = vehicleVOs
        for item in self.__list:
            storedItem = self.__listMapping.get(item['dbID'])
            if storedItem:
                item['selected'] = storedItem['selected']
            self.__listMapping[item['dbID']] = item

        self.refresh()

    def toggleSelectionByID(self, dbID):
        self.__listMapping[dbID]['selected'] = not self.__listMapping[dbID]['selected']
        self.refresh()

    def getSelected(self):
        return tuple((v['dbID'] for v in self.__listMapping.itervalues() if v['selected']))

    def getLastSortMethod(self):
        return self._sort

    def clear(self):
        self.__list = []
        self.__listMapping = {}

    def fini(self):
        self.clear()
        self._dispose()

    def __sortingMethod(self, item, field):
        valueGetter = self.__sortMapping[field]
        return valueGetter(item)
