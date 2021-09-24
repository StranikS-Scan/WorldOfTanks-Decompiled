# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/battle_carousel.py
import logging
import weakref
import BigWorld
import Event
from account_helpers.AccountSettings import EPICBATTLE_CAROUSEL_FILTER_1, EPICBATTLE_CAROUSEL_FILTER_2
from account_helpers.AccountSettings import EPICBATTLE_CAROUSEL_FILTER_CLIENT_1
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform import getButtonsAssetPath
from gui.Scaleform.daapi.view.common.filter_contexts import getFilterSetupContexts, FilterSetupContext
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_data_provider import CarouselDataProvider
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import CarouselFilter
from gui.Scaleform.daapi.view.meta.BattleTankCarouselMeta import BattleTankCarouselMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from helpers import dependency
from helpers.i18n import makeString as _ms
import nations
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.shared.respawn import respawn_utils
from gui.shared.gui_items import ItemsCollection
from skeletons.gui.shared.gui_items import IGuiItemsFactory
_logger = logging.getLogger(__name__)
_DISABLED_FILTERS = ['bonus']

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
     'vehicleLevelIcon': RES_ICONS.getLevelIcon(vehicle.level),
     'favorite': vehicle.isFavorite,
     'enabled': True,
     'cooldown': '',
     'settings': 0}


class BattleCarouselDataProvider(CarouselDataProvider):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, carouselFilter, itemsCache, currentVehicle):
        super(BattleCarouselDataProvider, self).__init__(carouselFilter, itemsCache, currentVehicle)
        self.__separatorItems = []
        self.__filteredSeparators = []
        self.__availableLevels = []
        self.__indexToScroll = -1

    @property
    def collection(self):
        return self._vehicleItems + self.__separatorItems

    def getCurrentVehiclesCount(self):
        result = super(BattleCarouselDataProvider, self).getCurrentVehiclesCount()
        return result - len(self.__filteredSeparators)

    def setShowStats(self, showVehicleStats):
        self._showVehicleStats = False

    def clear(self):
        super(BattleCarouselDataProvider, self).clear()
        self.__separatorItems = []
        self.__filteredSeparators = []
        self.__availableLevels = []
        self.__indexToScroll = -1

    def getIndexToScroll(self):
        return self.__indexToScroll

    def getAvailableLevels(self):
        return self.__availableLevels

    def applyFilter(self, forceApply=False):
        prevFilteredIndices = self._filteredIndices[:]
        prevSelectedIdx = self._selectedIdx
        self._filteredIndices = []
        self._selectedIdx = -1
        self.__indexToScroll = -1
        isSeparatorsNeeded = self.__isVehicleLevelsFilterNeeded()
        currentVehicleInvID = self._currentVehicle.invID
        vehLevelsToScroll = self.__getVehLevelsUnlockInBattle()
        visibleVehiclesIntCDs = [ vehicle.intCD for vehicle in self._getCurrentVehicles() ]
        sortedVehicleIndices = self._getSortedIndices()
        self.__filteredSeparators = []
        for idx in sortedVehicleIndices:
            vehicle = self._vehicles[idx]
            if vehicle.intCD in visibleVehiclesIntCDs:
                if isSeparatorsNeeded and vehicle.level not in self.__filteredSeparators:
                    separatorIdx = len(self._vehicles) + self.__availableLevels.index(vehicle.level)
                    if vehicle.level in vehLevelsToScroll:
                        self.__indexToScroll = len(self._filteredIndices)
                    self._filteredIndices.append(separatorIdx)
                    self.__filteredSeparators.append(vehicle.level)
                self._filteredIndices.append(idx)
                if currentVehicleInvID == vehicle.invID:
                    self._selectedIdx = len(self._filteredIndices) - 1

        self._filteredIndices += self._getAdditionalItemsIndexes()
        needUpdate = forceApply or prevFilteredIndices != self._filteredIndices or prevSelectedIdx != self._selectedIdx
        if needUpdate:
            self._filterByIndices()

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

    def _buildVehicleItems(self):
        super(BattleCarouselDataProvider, self)._buildVehicleItems()
        self.__calculateCountOfVehicleLevels()
        self.__buildSeparatorItems()

    def _buildVehicle(self, vehicle):
        rawVehicleData = self._itemsCache.getRawVehicleData(vehicle.invID)
        if rawVehicleData:
            vehicle.settings = rawVehicleData.settings
        return getEpicVehicleDataVO(vehicle)

    def _getVehicleStats(self, vehicle):
        return {}

    def _syncRandomStats(self):
        pass

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (vehicle.level,
         not vehicle.isFavorite,
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.userName)

    def __isVehicleLevelsFilterNeeded(self):
        return len(self.__availableLevels) > 1

    def __calculateCountOfVehicleLevels(self):
        self.__availableLevels = []
        for vehicle in self._vehicles:
            if vehicle.level not in self.__availableLevels:
                self.__availableLevels.append(vehicle.level)

        self.__availableLevels.sort()

    def __buildSeparatorItems(self):
        self.__separatorItems = []
        if not self.__isVehicleLevelsFilterNeeded():
            return
        for level in self.__availableLevels:
            self.__separatorItems.append({'levelInfo': {'level': level,
                           'isCollapsed': True,
                           'isCollapsible': False,
                           'infoText': ''}})

    @staticmethod
    def __getVehLevelsUnlockInBattle():
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is None:
            _logger.warning('Missing arena')
            return []
        else:
            return arena.settings.get('epic_config', {}).get('unlockableInBattleVehLevels', [])


class VehicleData(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self, carousel):
        self.items = self
        self.__carouselRef = weakref.ref(carousel)
        self.__vehicles = None
        self.__eManager = Event.EventManager()
        self.onSyncCompleted = Event.Event(self.__eManager)
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVehiclesUpdated += self.__updateRespawnVehicles
        return

    def dispose(self):
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVehiclesUpdated -= self.__updateRespawnVehicles
        self.__carouselRef = None
        self.__vehicles = None
        self.__eManager.clear()
        self.__eManager = None
        self.items = None
        return

    def isSynced(self):
        return True

    def getVehicles(self, criteria=None):
        result = ItemsCollection()
        if self.__vehicles:
            for invID, vehicleType in enumerate(self.__vehicles):
                vehicle = self.itemsFactory.createVehicle(typeCompDescr=vehicleType.intCD, inventoryID=invID)
                result[vehicle.intCD] = vehicle

        return result

    def getRawVehicleData(self, invID):
        return None if invID >= len(self.__vehicles) else self.__vehicles[invID]

    def __updateRespawnVehicles(self, vehs):
        self.__vehicles = vehs.values()
        carousel = self.__carouselRef()
        if carousel:
            carousel.latePopulate()
        self.onSyncCompleted()


class BattleTankCarousel(BattleTankCarouselMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleTankCarousel, self).__init__()
        self._carouselDPCls = BattleCarouselDataProvider
        self._carouselFilterCls = BattleCarouselFilter
        self.__vehicleData = VehicleData(self)
        self.__isUnlockedVehiclesShown = False

    def updateHotFilters(self):
        hotFilters = []
        for key in self._usedFilters:
            filter_ = self.filter.get(key)
            if key in _DISABLED_FILTERS:
                filter_ = False
            hotFilters.append(filter_)

        self.as_setCarouselFilterS({'hotFilters': hotFilters})

    def sortVehicles(self, _):
        self._carouselDP.applyFilter()

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
        self.updateVehicles(self.__vehicleData.getVehicles())
        self.updateAviability()

    def getCustomParams(self):
        return {'vehicleLevelsFilter': self._carouselDP.getAvailableLevels()}

    def show(self):
        indexToScroll = self._carouselDP.getIndexToScroll()
        if indexToScroll >= 0 and not self.__isUnlockedVehiclesShown:
            self.__isUnlockedVehiclesShown = True
            self.as_scrollToSlotS(indexToScroll)

    def _populate(self):
        super(BattleTankCarousel, self)._populate()
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self.as_useExtendedCarouselS(True)
        self.as_initCarouselFilterS(self._getInitialFilterVO(getFilterSetupContexts(1)))

    def _dispose(self):
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        self.__vehicleData.dispose()
        self.__vehicleData = None
        super(BattleTankCarousel, self)._dispose()
        return

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

    def _getFilters(self):
        pass

    def __onViewLoaded(self, view, *args):
        if view.settings.alias == BATTLE_VIEW_ALIASES.BATTLE_TANK_CAROUSEL_FILTER_POPOVER:
            view.setTankCarousel(self)
