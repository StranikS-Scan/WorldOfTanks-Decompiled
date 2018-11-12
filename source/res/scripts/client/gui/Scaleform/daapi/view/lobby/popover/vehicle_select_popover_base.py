# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/popover/vehicle_select_popover_base.py
import nations
from gui import GUI_NATIONS_ORDER_INDEX_REVERSED
from gui.Scaleform.daapi.view.meta.VehicleSelectPopoverMeta import VehicleSelectPopoverMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.shared.gui_items.Vehicle import VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED
from gui.shared.utils import sortByFields

class VehicleSelectPopoverBase(VehicleSelectPopoverMeta):

    def __init__(self, ctx=None):
        super(VehicleSelectPopoverBase, self).__init__(ctx)
        self._vehDP = None
        self._isMultiSelect = True
        if ctx is not None:
            data = ctx.get('data', None)
            self._isMultiSelect = data.isMultiSelect if data is not None else True
        return

    def setVehicleSelected(self, dbID, autoClose):
        self._vehDP.toggleSelectionByID(dbID)
        if autoClose:
            self.addButtonClicked()

    def onWindowClose(self):
        self.destroy()

    def _initDP(self):
        self._vehDP = VehiclesDataProvider(self._isMultiSelect)
        self._vehDP.setFlashObject(self.as_getTableDPS())

    def _dispose(self):
        super(VehicleSelectPopoverBase, self)._dispose()
        self._vehDP.fini()
        self._vehDP = None
        return

    def _updateSortField(self):
        sort = self._vehDP.getLastSortMethod()
        order = 'ascending' if sort[0][1] else 'descending'
        self.as_updateTableSortFieldS(sortField=sort[0][0], sortDirection=order)


class VehiclesDataProvider(SortableDAAPIDataProvider):

    def __init__(self, isMultiSelect=True):
        super(VehiclesDataProvider, self).__init__()
        self.__isMultiSelect = isMultiSelect
        self.__selectedDbID = 0
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
            if not self.__isMultiSelect and item['selected']:
                self.__selectedDbID = item['dbID']

        self.refresh()

    def toggleSelectionByID(self, dbID):
        if not self.__isMultiSelect:
            if self.__selectedDbID:
                self.__listMapping[self.__selectedDbID]['selected'] = False
            self.__selectedDbID = dbID
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
        self.destroy()

    def __sortingMethod(self, item, field):
        valueGetter = self.__sortMapping[field]
        return valueGetter(item)
