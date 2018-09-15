# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/event_boards_filter_vehicles_popover.py
import nations
from debug_utils import LOG_DEBUG
from gui import GUI_NATIONS_ORDER_INDEX_REVERSED
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import packHeaderColumnData
from gui.Scaleform.daapi.view.lobby.vehicle_selector_base import VehicleSelectorBase
from gui.Scaleform.daapi.view.meta.EventBoardsResultFilterVehiclesPopoverViewMeta import EventBoardsResultFilterVehiclesPopoverViewMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import getSmallIconPath, VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED
from gui.shared.utils import sortByFields
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache

class EventBoardsFilterVehiclesPopover(EventBoardsResultFilterVehiclesPopoverViewMeta, VehicleSelectorBase):
    itemsCache = dependency.descriptor(IItemsCache)
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self, ctx=None):
        super(EventBoardsFilterVehiclesPopover, self).__init__(ctx)
        self._vehDP = None
        self.__opener = None
        return

    def initFilters(self):
        filters = self._initFilter(nation=-1, vehicleType='none', isMain=False, level=-1, compatibleOnly=False)
        self._updateFilter(filters['nation'], filters['vehicleType'], filters['isMain'], filters['level'], filters['compatibleOnly'])
        return filters

    def applyFilters(self, nation, vehicleType, level, isMain, hangarOnly):
        self._updateFilter(nation, vehicleType, isMain, level, hangarOnly)
        self.updateData()

    def updateData(self):
        allVehicles = self.itemsCache.items.getVehicles()
        vehicles = self._updateData(allVehicles, compatiblePredicate=lambda vo: vo['inHangar'])
        self._vehDP.buildList(vehicles)
        self.__updateSortField()

    def onWindowClose(self):
        self.destroy()

    def setOpener(self, view):
        self.__opener = view

    def setVehicleSelected(self, dbID):
        LOG_DEBUG('EventBoardsFilterVehiclesPopover.setVehicleSelected', dbID)

    def _populate(self):
        super(EventBoardsFilterVehiclesPopover, self)._populate()
        self.__initControls()
        self._vehDP = VehiclesDataProvider()
        self._vehDP.setFlashObject(self.as_getTableDPS())
        self.updateData()

    def _dispose(self):
        super(EventBoardsFilterVehiclesPopover, self)._dispose()
        self._vehDP.fini()
        self._vehDP = None
        return

    def _makeVehicleVOAction(self, vehicle):
        iconFunc = RES_ICONS.maps_icons_vehicletypes_elite if vehicle.isPremium else RES_ICONS.maps_icons_vehicletypes
        return {'dbID': vehicle.intCD,
         'level': vehicle.level,
         'shortUserName': vehicle.shortUserName,
         'smallIconPath': getSmallIconPath(vehicle.name),
         'nationID': vehicle.nationID,
         'type': vehicle.type,
         'typeIcon': iconFunc(vehicle.type + '.png'),
         'inHangar': vehicle.isInInventory}

    def __initControls(self):
        common = {'enabled': True,
         'btnHeight': 34}
        headers = [packHeaderColumnData('nations', 45, icon=RES_ICONS.MAPS_ICONS_FILTERS_NATIONS_ALL, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_NATION, **common),
         packHeaderColumnData('type', 45, icon=RES_ICONS.MAPS_ICONS_FILTERS_TANKS_ALL, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_TYPE, **common),
         packHeaderColumnData('level', 45, icon=RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_LEVEL, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_LEVEL, **common),
         packHeaderColumnData('name', 130, label=VEH_COMPARE.ADDVEHPOPOVER_VEHICLENAME, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_TITLE, direction='ascending', **common),
         packHeaderColumnData('hangar', 45, icon=RES_ICONS.MAPS_ICONS_BUTTONS_ICON_TABLE_COMPARISON_INHANGAR, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_INHANGAR, **common)]
        self.as_setInitDataS({'tableHeaders': headers,
         'filters': self.initFilters(),
         'header': text_styles.highTitle(_ms(VEH_COMPARE.ADDVEHPOPOVER_HEADER))})

    def __updateSortField(self):
        sort = self._vehDP.getLastSortMethod()
        assert sort
        order = 'ascending' if sort[0][1] else 'descending'
        self.as_updateTableSortFieldS(sortField=sort[0][0], sortDirection=order)


class VehiclesDataProvider(SortableDAAPIDataProvider):

    def __init__(self):
        super(VehiclesDataProvider, self).__init__()
        self.__list = None
        self._sort = (('level', False),)
        self.__sortMapping = {'nations': lambda v: GUI_NATIONS_ORDER_INDEX_REVERSED[nations.NAMES[v['nationID']]],
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
            self.refresh()

    def buildList(self, vehicleVOs):
        self.__list = vehicleVOs
        self.refresh()

    def getLastSortMethod(self):
        return self._sort

    def clear(self):
        self.__list = []

    def fini(self):
        self.clear()
        self._dispose()

    def __sortingMethod(self, item, field):
        valueGetter = self.__sortMapping[field]
        return valueGetter(item)
