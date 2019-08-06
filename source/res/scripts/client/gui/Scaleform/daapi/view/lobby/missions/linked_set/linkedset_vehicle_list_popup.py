# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/linked_set/linkedset_vehicle_list_popup.py
from nations import AVAILABLE_NAMES
from gui.Scaleform.daapi.view.meta.VehicleListPopupMeta import VehicleListPopupMeta
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleBasicVO
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import LinkedSetEvent
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.formatters.vehicle_filters import packVehicleTypesFilter, packNationsFilter
from constants import VEHICLE_CLASSES, MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL
from helpers import dependency
from account_helpers.AccountSettings import AccountSettings
from skeletons.gui.shared import IItemsCache
_ALL_NATIONS = -1
_EXCLUDED_VEHICLE_CRITERIA = (~REQ_CRITERIA.IN_OWNERSHIP,
 ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR,
 ~REQ_CRITERIA.VEHICLE.PREMIUM,
 ~REQ_CRITERIA.VEHICLE.EVENT,
 ~REQ_CRITERIA.VEHICLE.SECRET)

class LinkedSetVehicleListPopup(VehicleListPopupMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(LinkedSetVehicleListPopup, self).__init__()
        ctx = ctx or {}
        self.__levelsRange = ctx.get('levelsRange', range(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1))
        self.__infoText = ctx.get('infoText', '')
        self.__section = ctx['section']
        self.__filters = {}

    def onWindowClose(self):
        self.destroy()

    def onSelectVehicles(self, vehicleCD):
        vehicleVO = makeVehicleBasicVO(self.itemsCache.items.getItemByCD(vehicleCD))
        ctx = {'vehicleCD': vehicleCD,
         'shortUserName': vehicleVO['shortUserName']}
        self.fireEvent(LinkedSetEvent(LinkedSetEvent.VEHICLE_SELECTED, ctx), EVENT_BUS_SCOPE.LOBBY)
        self.onWindowClose()

    def initFilters(self):
        filters = AccountSettings.getFilter(self.__section)
        filters = self._initFilter(filters['nation'], filters['vehicleType'])
        self.__filters['nation'] = filters['nation']
        self.__filters['vehicleType'] = filters['vehicleType']
        self.as_setFiltersDataS(filters)

    def applyFilters(self, nation, vehicleType):
        self.__filters['nation'] = nation
        self.__filters['vehicleType'] = vehicleType
        self.__updateData()

    def _initFilter(self, nation, vehicleType):
        vehicles = self.__getVehicles()
        nations = set((AVAILABLE_NAMES[vehicle['nationID']] for vehicle in vehicles))
        types = set((vehicle['type'] for vehicle in vehicles))
        if vehicles:
            self.__infoText = ''
        filtersData = {'vehicleTypesDP': packVehicleTypesFilter(defaultVehType='none', types=types),
         'nationDP': packNationsFilter(nations=nations),
         'nation': nation,
         'vehicleType': vehicleType}
        return filtersData

    def _populate(self):
        super(LinkedSetVehicleListPopup, self)._populate()
        self.initFilters()
        self.__updateData()

    def _dispose(self):
        super(LinkedSetVehicleListPopup, self)._dispose()
        AccountSettings.setFilter(self.__section, self.__filters)

    def __getVehicles(self, nation=_ALL_NATIONS, vehicleType='none'):
        criteria = REQ_CRITERIA.VEHICLE.LEVELS(self.__levelsRange)
        for crit in _EXCLUDED_VEHICLE_CRITERIA:
            criteria |= crit

        if nation != _ALL_NATIONS:
            criteria |= REQ_CRITERIA.NATIONS([self.__filters['nation']])
        if vehicleType != 'none':
            criteria |= REQ_CRITERIA.VEHICLE.CLASSES([self.__filters['vehicleType']])
        vehicles = self.itemsCache.items.getVehicles(criteria)
        return [ makeVehicleBasicVO(v, self.__levelsRange, VEHICLE_CLASSES) for v in vehicles.itervalues() ]

    def __updateData(self):
        vehicles = self.__getVehicles(self.__filters['nation'], self.__filters['vehicleType'])
        if vehicles:
            vehicles.sort(key=lambda vehicle: (vehicle['nationID'], vehicle['typeIndex'], vehicle['shortUserName']))
            self.as_setListDataS(vehicles, None)
        else:
            self.as_setInfoTextS(self.__infoText)
        return
