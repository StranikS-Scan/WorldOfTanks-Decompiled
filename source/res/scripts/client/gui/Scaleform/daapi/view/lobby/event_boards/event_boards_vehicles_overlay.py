# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/event_boards_vehicles_overlay.py
from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_vos import makeFiltersVO, makeVehicleVO
from gui.Scaleform.daapi.view.lobby.event_boards.event_helpers import LEVELS_RANGE
from gui.Scaleform.daapi.view.meta.EventBoardsVehiclesOverlayMeta import EventBoardsVehiclesOverlayMeta
from gui.Scaleform.locale.EVENT_BOARDS import EVENT_BOARDS
from gui.event_boards.event_boards_items import EVENT_TYPE
from gui.shared.formatters.vehicle_filters import packVehicleTypesFilter, packVehicleLevelsFilter, packNationsFilter
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import int2roman, dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.shared import IItemsCache

class EventBoardsVehiclesOverlay(EventBoardsVehiclesOverlayMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    __lid = None
    __opener = None
    __filters = {'nation': -1,
     'vehicleType': 'none',
     'isMain': False,
     'level': -1,
     'compatibleOnly': False}

    def setOpener(self, view):
        self.__opener = view
        eventData = self.__opener.eventData
        if eventData.getType() == EVENT_TYPE.VEHICLE:
            filtersVO = self.__filters.copy()
            filtersVO['vehicleTypesDP'] = packVehicleTypesFilter(defaultVehType='none')
            filtersVO['levelsDP'] = packVehicleLevelsFilter(LEVELS_RANGE)
            filtersVO['nationDP'] = packNationsFilter()
            self.as_setFiltersS(filtersVO)
            self.applyFilters(**self.__filters)
        else:
            leaderboards = eventData.getLeaderboards()
            leaderboardID = leaderboards[0][0]
            header = {'filters': makeFiltersVO(eventData.getType(), leaderboards, leaderboardID, category='vehicles')}
            self.as_setHeaderS(header)
            self.changeFilter(leaderboardID)

    def changeFilter(self, lid):
        self.__lid = int(lid)
        self._setData()

    def applyFilters(self, nation, vehicleType, level, isMain, compatibleOnly):
        self.__filters = {'nation': nation,
         'vehicleType': vehicleType,
         'isMain': isMain,
         'level': level,
         'compatibleOnly': compatibleOnly}
        self._setData()

    def _setData(self):
        eventData = self.__opener.eventData
        eventType = eventData.getType()
        criteria = REQ_CRITERIA.EMPTY
        if eventType == EVENT_TYPE.VEHICLE:
            vehicleIds = [ veh for _, veh in eventData.getLeaderboards() ]
            title = _ms(EVENT_BOARDS.VEHICLES_VEHICLE)
            bgPath = None
            if self.__filters['nation'] != -1:
                criteria |= REQ_CRITERIA.NATIONS([self.__filters['nation']])
            if self.__filters['vehicleType'] != 'none':
                criteria |= REQ_CRITERIA.VEHICLE.CLASSES([self.__filters['vehicleType']])
            if self.__filters['isMain']:
                criteria |= REQ_CRITERIA.VEHICLE.FAVORITE
            if self.__filters['level'] != -1:
                criteria |= REQ_CRITERIA.VEHICLE.LEVELS([self.__filters['level']])
        else:
            vehicleIds = eventData.getLimits().getVehicles(self.__lid)
            leaderboard = eventData.getLeaderboard(self.__lid)
            if eventType == EVENT_TYPE.NATION:
                title = _ms('#menu:nation_tree/title/{}'.format(leaderboard))
                bgPath = '../maps/icons/eventBoards/flagsOverlay/{}.png'.format(leaderboard)
            elif eventType == EVENT_TYPE.LEVEL:
                title = _ms(EVENT_BOARDS.VEHICLES_LEVEL, level=int2roman(leaderboard))
                bgPath = None
            elif eventType == EVENT_TYPE.CLASS:
                title = _ms('#quests:classes/{}'.format(leaderboard))
                bgPath = None
            else:
                title = None
                bgPath = None
        allVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.IN_CD_LIST(vehicleIds))
        vehicles = allVehicles.filter(criteria).values()
        vehicles.sort(key=lambda v: v.isInInventory, reverse=True)
        vehiclesVO = [ makeVehicleVO(vehicle) for vehicle in vehicles ]
        data = {'title': title,
         'bgPath': bgPath,
         'vehicles': vehiclesVO}
        self.as_setVehiclesS(data)
        return
