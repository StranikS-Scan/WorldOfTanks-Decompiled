# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/battle_carousel.py
from account_helpers.AccountSettings import EPICBATTLE_CAROUSEL_FILTER_1, EPICBATTLE_CAROUSEL_FILTER_2
from account_helpers.AccountSettings import EPICBATTLE_CAROUSEL_FILTER_CLIENT_1
from gui.Scaleform import getButtonsAssetPath
from gui.Scaleform.daapi.view.common.filter_contexts import getFilterSetupContexts, FilterSetupContext
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_data_provider import CarouselDataProvider
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import CarouselFilter
from gui.Scaleform.daapi.view.meta.BattleTankCarouselMeta import BattleTankCarouselMeta
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from helpers.i18n import makeString as _ms
import nations
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.shared.respawn import respawn_utils
from gui.shared.gui_items import ItemsCollection
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from Event import Event
_DISABLED_FILTERS = ['bonus']
_BATTLE_CAROUSEL_FILTERS = ('favorite',)

class BattleCarouselFilter(CarouselFilter):

    def __init__(self):
        super(BattleCarouselFilter, self).__init__()
        self._serverSections = (EPICBATTLE_CAROUSEL_FILTER_1, EPICBATTLE_CAROUSEL_FILTER_2)
        self._clientSections = (EPICBATTLE_CAROUSEL_FILTER_CLIENT_1,)

    def save(self):
        pass


def getEpicVehicleDataVO(vehicle):
    return {'vehicleID': vehicle.intCD,
     'vehicleName': vehicle.shortUserName if vehicle.isPremiumIGR else vehicle.userName,
     'flagIcon': respawn_utils.FLAG_ICON_TEMPLATE % nations.NAMES[vehicle.nationID],
     'vehicleIcon': vehicle.icon,
     'vehicleTypeIcon': (respawn_utils.VEHICLE_ELITE_TYPE_TEMPLATE if vehicle.isElite else respawn_utils.VEHICLE_TYPE_TEMPLATE) % vehicle.type,
     'isElite': vehicle.isElite,
     'isPremium': vehicle.isPremium,
     'vehicleLevelIcon': respawn_utils.VEHICLE_LEVEL_TEMPLATE % vehicle.level,
     'favorite': vehicle.isFavorite,
     'enabled': True,
     'cooldown': '',
     'settings': 0}


class BattleCarouselDataProvider(CarouselDataProvider):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def setShowStats(self, showVehicleStats):
        self._showVehicleStats = False

    def getVehicles(self):
        return self._vehicles

    def _buildVehicle(self, vehicle):
        rawVehicleData = self._itemsCache.getRawVehicleData(vehicle.invID)
        if rawVehicleData:
            vehicle.settings = rawVehicleData.settings
        result = getEpicVehicleDataVO(vehicle)
        return result

    def _getVehicleStats(self, vehicle):
        return {}

    def _syncRandomStats(self):
        pass

    def updateVehicleStates(self, slotsStatesData):
        updateIndices = []
        updateVehicles = []
        for data in slotsStatesData:
            for idx, oldVehicle in enumerate(self._vehicles):
                if oldVehicle.intCD == data['vehicleID']:
                    curVO = self._vehicleItems[idx]
                    if curVO['enabled'] != data['enabled'] or curVO['cooldown'] != data['cooldown']:
                        updateIndices.append(idx)
                        updateVehicles.append(data)
                        self._vehicleItems[idx].update(data)
                    break

        if updateIndices:
            self.flashObject.invalidateItems(updateIndices, updateVehicles)

    def selectVehicle(self, filteredIdx):
        realIdx = self._filteredIndices[filteredIdx]
        vehicle = self._vehicles[realIdx]
        self._selectedIdx = filteredIdx
        self._currentVehicle = vehicle
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.chooseVehicleForRespawn(vehicle.intCD)
        return

    def getSelectedVehicle(self):
        return self._currentVehicle

    def selectVehicleByID(self, vehicleID):
        for vehicle in self._vehicles:
            if vehicle.intCD == vehicleID:
                self._currentVehicle = vehicle
                self._selectedIdx = -1

        self.applyFilter()

    def sortVehicles(self, vehList):
        newVehicles = []
        newVehicleItems = []
        updateIndices = []
        for newIdx, newVehicle in enumerate(vehList):
            for idx, oldVehicle in enumerate(self._vehicles):
                if oldVehicle.intCD == newVehicle.intCD:
                    newVehicles.append(self._vehicles[idx])
                    newVehicleItems.append(self._vehicleItems[idx])
                    updateIndices.append(newIdx)
                    break

        self.flashObject.invalidateItems(updateIndices, newVehicleItems)
        self._vehicles = newVehicles
        self._vehicleItems = newVehicleItems
        self.applyFilter()

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        pass


class VehicleData(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self, carousel):
        self.items = self
        self.onSyncCompleted = Event()
        self.__carousel = carousel
        self.__vehicles = None
        ctrl = self.sessionProvider.dynamic.respawn
        ctrl.onRespawnVehiclesUpdated += self.__updateVehiclesList
        return

    def getVehicles(self, criteria=None):
        result = ItemsCollection()
        if self.__vehicles:
            for invID, vehicleType in enumerate(self.__vehicles):
                vehicle = self.itemsFactory.createVehicle(typeCompDescr=vehicleType.intCD, inventoryID=invID)
                result[vehicle.intCD] = vehicle

        return result

    def dispose(self):
        ctrl = self.sessionProvider.dynamic.respawn
        ctrl.onRespawnVehiclesUpdated -= self.__updateVehiclesList

    def getRawVehicleData(self, invID):
        return None if invID >= len(self.__vehicles) else self.__vehicles[invID]

    def __updateVehiclesList(self, vehicleList):
        self.__vehicles = vehicleList
        self.__carousel.latePopulate()
        self.onSyncCompleted()


class BattleTankCarousel(BattleTankCarouselMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleTankCarousel, self).__init__()
        self._carouselDPCls = BattleCarouselDataProvider
        self._carouselFilterCls = BattleCarouselFilter
        self._usedFilters = _BATTLE_CAROUSEL_FILTERS
        self.__vehicleData = VehicleData(self)

    def updateHotFilters(self):
        hotFilters = []
        for key in self._usedFilters:
            filter_ = self.filter.get(key)
            if key in _DISABLED_FILTERS:
                filter_ = False
            hotFilters.append(filter_)

        self.as_setCarouselFilterS({'hotFilters': hotFilters})

    def sortVehicles(self, vehList):
        self._carouselDP.sortVehicles(vehList)

    def resetFilters(self):
        super(BattleTankCarousel, self).resetFilters()
        self.updateHotFilters()

    def setFilter(self, idx):
        self.filter.switch(self._usedFilters[idx])
        self.blinkCounter()
        self.applyFilter()

    def updateVehicleStates(self, slotsStatesData):
        self._carouselDP.updateVehicleStates(slotsStatesData)

    def getSelectedVehicle(self):
        if not self._carouselDP:
            return None
        else:
            vehicle = self._carouselDP.getSelectedVehicle()
            return None if not hasattr(vehicle, 'intCD') else vehicle

    def selectVehicleByID(self, vehicleID):
        self._carouselDP.selectVehicleByID(vehicleID)

    def latePopulate(self):
        self.updateVehicles()
        self._carouselDP.buildList()
        self.updateAviability()
        self.resetFilters()

    def _populate(self):
        super(BattleTankCarousel, self)._populate()
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self.as_initCarouselFilterS(self._getInitialFilterVO(getFilterSetupContexts(1)))

    def _dispose(self):
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        self.__vehicleData.dispose()
        super(BattleTankCarousel, self)._dispose()

    def _initDataProvider(self):
        self._carouselDPConfig.update({'carouselFilter': self._carouselFilterCls(),
         'itemsCache': self.__vehicleData,
         'currentVehicle': self._currentVehicle})
        self._carouselDP = self._carouselDPCls(**self._carouselDPConfig)

    def _getFiltersVisible(self):
        return True

    def _getInitialFilterVO(self, contexts):
        filters = self.filter.getFilters(self._usedFilters)
        filtersVO = {'mainBtn': {'value': getButtonsAssetPath('params'),
                     'tooltip': '#tank_carousel_filter:tooltip/params'},
         'hotFilters': [],
         'isVisible': self._getFiltersVisible()}
        for entry in self._usedFilters:
            filterCtx = contexts.get(entry, FilterSetupContext())
            filtersVO['hotFilters'].append({'id': entry,
             'value': getButtonsAssetPath(filterCtx.asset or entry),
             'selected': filters[entry],
             'enabled': True,
             'tooltip': makeTooltip('#tank_carousel_filter:tooltip/{}/header'.format(entry), _ms('#tank_carousel_filter:tooltip/{}/body'.format(entry), **filterCtx.ctx))})

        length = len(filtersVO['hotFilters'])
        for id_ in range(0, length):
            entry = filtersVO['hotFilters'][id_]
            if entry['id'] in _DISABLED_FILTERS:
                entry['enabled'] = False
                entry['selected'] = False

        return filtersVO

    def __onViewLoaded(self, view, *args):
        if view.settings.alias == BATTLE_VIEW_ALIASES.BATTLE_TANK_CAROUSEL_FILTER_POPOVER:
            view.setTankCarousel(self)
