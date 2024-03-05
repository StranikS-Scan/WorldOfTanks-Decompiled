# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/select_vehicle_popover.py
import nations
from gui import GUI_NATIONS_ORDER_INDEX_REVERSED
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import packHeaderColumnData
from gui.Scaleform.daapi.view.lobby.vehicle_selector_base import VehicleSelectorBase
from gui.Scaleform.daapi.view.meta.StorageVehicleSelectPopoverMeta import StorageVehicleSelectPopoverMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.Scaleform.locale.TANK_CAROUSEL_FILTER import TANK_CAROUSEL_FILTER
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED
from gui.shared.gui_items.Vehicle import getSmallIconPath, getTypeSmallIconPath
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils import sortByFields
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.shared import IItemsCache
_SEARCH_INPUT_MAX_CHARS = 50

def _makeVehicleCmpVO(vehicle):
    return {'intCD': vehicle.intCD,
     'level': vehicle.level,
     'shortUserName': vehicle.shortUserName,
     'smallIconPath': getSmallIconPath(vehicle.name),
     'nationIcon': RES_ICONS.getFilterNation(vehicle.nationName),
     'typeIcon': getTypeSmallIconPath(vehicle.type, vehicle.isPremium),
     'nationID': vehicle.nationID,
     'type': vehicle.type}


class VehicleSelectPopoverStorage(StorageVehicleSelectPopoverMeta):

    def __init__(self, ctx=None):
        super(VehicleSelectPopoverStorage, self).__init__(ctx)
        self._vehDP = None
        return

    def onWindowClose(self):
        self.destroy()

    def _initDP(self):
        self._vehDP = VehiclesDataProvider()
        self._vehDP.setFlashObject(self.as_getTableDPS())

    def _dispose(self):
        super(VehicleSelectPopoverStorage, self)._dispose()
        self._vehDP.fini()
        self._vehDP = None
        return

    def _updateSortField(self):
        sort = self._vehDP.getLastSortMethod()
        order = 'ascending' if sort[0][1] else 'descending'
        self.as_updateTableSortFieldS(sortField=sort[0][0], sortDirection=order)


class VehicleSelectPopover(VehicleSelectPopoverStorage, VehicleSelectorBase):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(VehicleSelectPopover, self).__init__(ctx)
        self._searchStr = ''

    def applyFilters(self, nation, vehicleType, level, isMain):
        self._updateFilter(nation, vehicleType, isMain, level)
        self.updateData()

    def updateData(self):
        criteria = REQ_CRITERIA.INVENTORY
        criteria |= REQ_CRITERIA.VEHICLE.NAME_VEHICLE(self._searchStr)
        criteria |= ~REQ_CRITERIA.VEHICLE.IS_STORAGE_HIDDEN
        criteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
        criteria |= ~REQ_CRITERIA.VEHICLE.MAPS_TRAINING
        criteria |= ~REQ_CRITERIA.VEHICLE.HIDDEN_IN_HANGAR
        allVehicles = self._itemsCache.items.getVehicles(criteria)
        vehicles = self._updateData(allVehicles)
        self._vehDP.buildList(vehicles)
        if self._vehDP.collection:
            self.as_showDummyS(False)
        else:
            self.as_showDummyS(True)
        self._updateSortField()

    def setVehicleSelected(self, dbID, autoClose):
        self.fireEvent(events.StorageEvent(events.StorageEvent.VEHICLE_SELECTED, ctx={'vehicleId': dbID}), scope=EVENT_BUS_SCOPE.LOBBY)
        self.onWindowClose()

    def changeSearchNameVehicle(self, inputText):
        self._searchStr = inputText
        self.updateData()

    def initFilters(self):
        filters = self._initFilter()
        self._updateFilter(filters['nation'], filters['vehicleType'], filters['isMain'], filters['level'], filters['compatibleOnly'])
        return filters

    def _populate(self):
        super(VehicleSelectPopover, self)._populate()
        self.__initControls()
        self._initDP()
        self.__updateSearchInput()
        self.updateData()

    def __updateSearchInput(self):
        searchInputTooltip = makeTooltip(TANK_CAROUSEL_FILTER.TOOLTIP_SEARCHINPUT_HEADER, _ms(TANK_CAROUSEL_FILTER.TOOLTIP_SEARCHINPUT_BODY, count=_SEARCH_INPUT_MAX_CHARS))
        searchInputLabel = _ms(TANK_CAROUSEL_FILTER.POPOVER_LABEL_SEARCHNAMEVEHICLE)
        self.as_updateSearchS(searchInputLabel, '', searchInputTooltip, _SEARCH_INPUT_MAX_CHARS)

    def _makeVehicleVOAction(self, vehicle):
        return _makeVehicleCmpVO(vehicle)

    def __initControls(self):
        common = {'btnHeight': 34,
         'enabled': True}
        headers = [packHeaderColumnData('nations', 45, icon=RES_ICONS.MAPS_ICONS_FILTERS_NATIONS_ALL, tooltip=STORAGE.VEHICLESELECTPOPOVER_TOOLTIPS_NATION, **common),
         packHeaderColumnData('type', 45, icon=RES_ICONS.MAPS_ICONS_FILTERS_TANKS_ALL, tooltip=STORAGE.VEHICLESELECTPOPOVER_TOOLTIPS_TYPE, **common),
         packHeaderColumnData('level', 45, icon=RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_LEVEL, tooltip=STORAGE.VEHICLESELECTPOPOVER_TOOLTIPS_LEVEL, **common),
         packHeaderColumnData('name', 210, label=STORAGE.VEHICLESELECTPOPOVER_VEHICLENAME, tooltip=STORAGE.VEHICLESELECTPOPOVER_TOOLTIPS_TITLE, direction='ascending', **common)]
        self.as_setInitDataS({'tableHeaders': headers,
         'filters': self.initFilters(),
         'header': text_styles.highTitle(_ms(STORAGE.STORAGE_VEHICLESELECTPOPOVER_LABEL))})


class VehiclesDataProvider(SortableDAAPIDataProvider):

    def __init__(self):
        super(VehiclesDataProvider, self).__init__()
        self.__list = None
        self._sort = (('level', False),)
        self.__sortMapping = {'check': lambda v: v['selected'],
         'nations': lambda v: GUI_NATIONS_ORDER_INDEX_REVERSED[nations.NAMES[v['nationID']]],
         'type': lambda v: VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED[v['type']],
         'level': lambda v: v['level'] << 16 | GUI_NATIONS_ORDER_INDEX_REVERSED[nations.NAMES[v['nationID']]] << 8 | VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED[v['type']],
         'name': lambda v: v['shortUserName']}
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
        self.refresh()

    def getLastSortMethod(self):
        return self._sort

    def clear(self):
        self.__list = []

    def fini(self):
        self.clear()
        self.destroy()

    def __sortingMethod(self, item, field):
        valueGetter = self.__sortMapping[field]
        return valueGetter(item)
