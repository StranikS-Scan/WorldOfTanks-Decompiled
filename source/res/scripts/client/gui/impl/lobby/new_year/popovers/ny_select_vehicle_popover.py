# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/popovers/ny_select_vehicle_popover.py
import nations
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleBasicVO
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import packHeaderColumnData
from gui.Scaleform.daapi.view.lobby.vehicle_selector_base import VehicleSelectorBase
from gui.Scaleform.daapi.view.meta.NYSelectVehiclePopoverMeta import NYSelectVehiclePopoverMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle, VEHICLE_TABLE_TYPES_ORDER_INDICES
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils import sortByFields
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.requesters.ItemsRequester import RESEARCH_CRITERIA
from helpers import dependency
from new_year.vehicle_branch_helpers import getAvailableVehicleRange
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
_INACCESSIBLE_FOR_TRADE_STATES = (Vehicle.VEHICLE_STATE.DAMAGED,
 Vehicle.VEHICLE_STATE.EXPLODED,
 Vehicle.VEHICLE_STATE.DESTROYED,
 Vehicle.VEHICLE_STATE.BATTLE,
 Vehicle.VEHICLE_STATE.IN_PREBATTLE,
 Vehicle.VEHICLE_STATE.LOCKED,
 Vehicle.VEHICLE_STATE.DISABLED)

class NySelectVehiclePopover(VehicleSelectorBase, NYSelectVehiclePopoverMeta):
    _itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, ctx=None):
        VehicleSelectorBase.__init__(self)
        NYSelectVehiclePopoverMeta.__init__(self)
        self._levelsRange = getAvailableVehicleRange()

    def initFilters(self):
        filters = self._initFilter(nation=-1, vehicleType='none', isMain=False, level=-1, compatibleOnly=False)
        self._updateFilter(filters['nation'], filters['vehicleType'], filters['isMain'], filters['level'], filters['compatibleOnly'])
        return filters

    def applyFilters(self, nation, vehicleType, level):
        self._updateFilter(nation, vehicleType, False, level)
        self.__updateData()

    def onWindowClose(self):
        self.destroy()

    def onSelectVehicle(self, vehicleCD):
        pass

    def _populate(self):
        super(NySelectVehiclePopover, self)._populate()
        self.__vehicleDP = NySelectVehiclePopoverDataProvider()
        self.__vehicleDP.setFlashObject(self.as_getDPS())
        self._itemsCache.onSyncCompleted += self.__onResync
        self.__initControls()
        self.__updateData()

    def _dispose(self):
        self._itemsCache.onSyncCompleted -= self.__onResync
        self.__vehicleDP.fini()
        self.__vehicleDP = None
        super(NySelectVehiclePopover, self)._dispose()
        return

    def _makeVehicleVOAction(self, vehicle):
        return makeVehicleBasicVO(vehicle)

    def __initControls(self):
        headers = [packHeaderColumnData('nations', 40, 40, tooltip=DIALOGS.TRADEINPOPOVER_SORTING_NATION, icon=RES_ICONS.MAPS_ICONS_FILTERS_NATIONS_ALL, enabled=True),
         packHeaderColumnData('type', 40, 40, tooltip=DIALOGS.TRADEINPOPOVER_SORTING_VEHTYPE, icon=RES_ICONS.MAPS_ICONS_FILTERS_TANKS_ALL, enabled=True),
         packHeaderColumnData('level', 40, 40, tooltip=DIALOGS.TRADEINPOPOVER_SORTING_VEHLVL, icon=RES_ICONS.MAPS_ICONS_FILTERS_LEVELS_LEVEL_ALL, enabled=True),
         packHeaderColumnData('shortUserName', 152, 40, label=DIALOGS.TRADEINPOPOVER_SORTING_VEHNAME_HEADER, tooltip=DIALOGS.TRADEINPOPOVER_SORTING_VEHNAME, enabled=True, verticalTextAlign='center', showSeparator=False)]
        if not self._nyController.isPostEvent():
            description = ''
            cooldown = 1
            if cooldown > 0:
                timeLeft = backport.getTillTimeStringByRClass(cooldown, R.strings.menu.Time.timeValueShort)
                description = backport.text(R.strings.ny.vehiclesView.selectVehiclePopover.description(), time=text_styles.stats(timeLeft))
        else:
            description = backport.text(R.strings.ny.vehiclesView.selectVehiclePopover.postEvent.description())
        self.as_setInitDataS({'title': backport.text(R.strings.ny.vehiclesView.selectVehiclePopover.header(), level=1),
         'description': description,
         'defaultSortField': 'level',
         'defaultSortDirection': 'descending',
         'tableHeaders': headers,
         'filters': self.initFilters()})

    def __onResync(self, reason, diff):
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC or GUI_ITEM_TYPE.VEHICLE in diff:
            self.__vehicleDP.clear()
            self.__updateData()

    def __updateData(self):
        allVehicles = self._itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(self._levelsRange) | ~REQ_CRITERIA.VEHICLE.IS_IN_BATTLE | ~REQ_CRITERIA.VEHICLE.IS_IN_UNIT | ~REQ_CRITERIA.VEHICLE.RENT | RESEARCH_CRITERIA.VEHICLE_TO_UNLOCK ^ (REQ_CRITERIA.VEHICLE.PREMIUM | REQ_CRITERIA.VEHICLE.SPECIAL))
        vehicles = self._updateData(allVehicles, compatiblePredicate=lambda vo: vo['inHangar'])
        self.__vehicleDP.buildList(vehicles)


class NySelectVehiclePopoverDataProvider(SortableDAAPIDataProvider):

    def __init__(self):
        super(NySelectVehiclePopoverDataProvider, self).__init__()
        self.__list = []
        self._sort = (('nations', True), ('type', False))
        self.__sortMapping = {'nations': lambda v: GUI_NATIONS_ORDER_INDEX[nations.NAMES[v['nationID']]],
         'type': lambda v: VEHICLE_TABLE_TYPES_ORDER_INDICES[v['type']],
         'level': lambda v: v['level'],
         'name': lambda v: v['shortUserName']}

    @property
    def collection(self):
        return self.__list

    @property
    def sortedCollection(self):
        return sortByFields(self._sort, self.__list, self.__sortingMethod)

    def emptyItem(self):
        return None

    def pySortOn(self, fields, order):
        super(NySelectVehiclePopoverDataProvider, self).pySortOn(fields, order)
        self.refresh()

    def clear(self):
        self.__list = []

    def fini(self):
        self.clear()
        self.destroy()

    def buildList(self, vehicleVOs):
        self.__list = vehicleVOs
        self.refresh()

    def __sortingMethod(self, item, field):
        valueGetter = self.__sortMapping[field]
        return valueGetter(item)
