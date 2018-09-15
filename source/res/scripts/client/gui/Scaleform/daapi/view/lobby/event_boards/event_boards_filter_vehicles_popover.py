# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/event_boards_filter_vehicles_popover.py
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_vos import makeVehiclePopoverVO, vehicleValueGetter
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import packHeaderColumnData
from gui.Scaleform.daapi.view.lobby.vehicle_selector_base import VehicleSelectorBase
from gui.Scaleform.daapi.view.meta.EventBoardsResultFilterVehiclesPopoverViewMeta import EventBoardsResultFilterVehiclesPopoverViewMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.EVENT_BOARDS import EVENT_BOARDS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.shared.formatters import text_styles
from gui.shared.utils import sortByFields
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.shared import IItemsCache

class EventBoardsFilterVehiclesPopover(EventBoardsResultFilterVehiclesPopoverViewMeta, VehicleSelectorBase):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(EventBoardsFilterVehiclesPopover, self).__init__(ctx)
        data = ctx.get('data')
        self.caller = data.caller if data else None
        self.eventID = data.eventID if data else None
        self._vehDP = None
        self.__eventData = None
        self.__onChangeFilter = None
        self.__selectedVehicleCD = None
        return

    def initFilters(self):
        filters = self._initFilter(nation=-1, vehicleType='none', isMain=False, level=-1, compatibleOnly=False)
        self._updateFilter(filters['nation'], filters['vehicleType'], filters['isMain'], filters['level'], filters['compatibleOnly'])
        return filters

    def applyFilters(self, nation, vehicleType, level, isMain, hangarOnly):
        self._updateFilter(nation, vehicleType, isMain, level, hangarOnly)
        self.updateData()

    def updateData(self):
        vehicleIds = [ veh for _, veh in self.__eventData.getLeaderboards() ]
        allVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.IN_CD_LIST(vehicleIds))
        vehicles = self._updateData(allVehicles, compatiblePredicate=lambda vo: vo['inHangar'])
        self._vehDP.buildList(vehicles, self.__selectedVehicleCD)
        self.__updateSortField()

    def onWindowClose(self):
        self.destroy()

    def setData(self, eventData, onApply, leaderboardID=None):
        self.__eventData = eventData
        self.__onChangeFilter = onApply
        if leaderboardID is None:
            currentVehicleCD = g_currentVehicle.item.intCD if g_currentVehicle.item else None
            self.__selectedVehicleCD = currentVehicleCD
        else:
            self.__selectedVehicleCD = eventData.getLeaderboard(leaderboardID)
        self.updateData()
        return

    def setVehicleSelected(self, dbID):
        lid = self.__eventData.getLeaderboardID(dbID)
        self.__onChangeFilter(lid)

    def resetFilters(self):
        self.__initControls()

    def _populate(self):
        super(EventBoardsFilterVehiclesPopover, self)._populate()
        self.__initControls()
        self._vehDP = VehiclesDataProvider()
        self._vehDP.setFlashObject(self.as_getTableDPS())

    def _dispose(self):
        super(EventBoardsFilterVehiclesPopover, self)._dispose()
        self._vehDP.fini()
        self._vehDP = None
        self.__eventData = None
        self.__onChangeFilter = None
        self.__selectedVehicleCD = None
        return

    def _makeVehicleVOAction(self, vehicle):
        return makeVehiclePopoverVO(vehicle)

    def __initControls(self):
        common = {'enabled': True,
         'btnHeight': 34}
        headers = [packHeaderColumnData('nations', 45, icon=RES_ICONS.MAPS_ICONS_FILTERS_NATIONS_ALL, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_NATION, **common),
         packHeaderColumnData('type', 45, icon=RES_ICONS.MAPS_ICONS_FILTERS_TANKS_ALL, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_TYPE, **common),
         packHeaderColumnData('level', 45, icon=RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_LEVEL, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_LEVEL, **common),
         packHeaderColumnData('name', 130, label=VEH_COMPARE.ADDVEHPOPOVER_VEHICLENAME, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_TITLE, direction='ascending', **common),
         packHeaderColumnData('hangar', 45, icon=RES_ICONS.MAPS_ICONS_BUTTONS_ICON_TABLE_COMPARISON_INHANGAR, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_INHANGAR, **common)]
        if self.caller == 'awards':
            okButtonLabel = EVENT_BOARDS.POPOVER_BUTTONS_SELECT
        else:
            okButtonLabel = EVENT_BOARDS.POPOVER_BUTTONS_RATING
        self.as_setInitDataS({'tableHeaders': headers,
         'filters': self.initFilters(),
         'header': text_styles.highTitle(_ms(EVENT_BOARDS.POPOVER_TITLE_VEHICLE)),
         'okButtonLabel': _ms(okButtonLabel)})

    def __updateSortField(self):
        sort = self._vehDP.getLastSortMethod()
        assert sort
        order = 'ascending' if sort[0][1] else 'descending'
        self.as_updateTableSortFieldS(sortField=sort[0][0], sortDirection=order)


class VehiclesDataProvider(SortableDAAPIDataProvider):

    def __init__(self):
        super(VehiclesDataProvider, self).__init__()
        self.__list = []
        self._sort = (('level', False), ('nations', True), ('type', True))

    @property
    def sortedCollection(self):
        return self.__list

    @property
    def collection(self):
        return self.__list

    def emptyItem(self):
        return None

    def pySortOn(self, fields, order):
        if fields == ['level']:
            fields = (fields[0], 'nations', 'type')
            order = (order[0], True, True)
        super(VehiclesDataProvider, self).pySortOn(fields, order)
        self.__sort()
        self.refresh()

    def buildList(self, vehicleVOs, selected=None):
        self.__list = vehicleVOs
        self.__sort()
        self.__selectVehicle(selected)
        self.refresh()

    def getLastSortMethod(self):
        return self._sort

    def clear(self):
        self.__list = []

    def fini(self):
        self.clear()
        self._dispose()

    def __sort(self):
        self.__list = sortByFields(self._sort, self.__list, vehicleValueGetter)

    def __selectVehicle(self, vehCD):
        ids = [ vo['dbID'] for vo in self.__list ]
        if ids and vehCD not in ids:
            vehCD = ids[0]
        for vo in self.__list:
            vo['selected'] = vo['dbID'] == vehCD
