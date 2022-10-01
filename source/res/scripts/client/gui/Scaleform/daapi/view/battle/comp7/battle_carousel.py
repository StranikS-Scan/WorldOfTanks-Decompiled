# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/comp7/battle_carousel.py
import logging
import typing
from collections import namedtuple
import BigWorld
from account_helpers.AccountSettings import COMP7_CAROUSEL_FILTER_1, COMP7_CAROUSEL_FILTER_2, AccountSettings
from account_helpers.AccountSettings import COMP7_CAROUSEL_FILTER_CLIENT_1
from constants import REQUEST_COOLDOWN, ARENA_PERIOD
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform import getButtonsAssetPath
from gui.Scaleform.daapi.view.battle.comp7.common import getSavedRowCountValue, rowValueToRowCount
from gui.Scaleform.daapi.view.common.filter_contexts import getFilterSetupContexts, FilterSetupContext
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_data_provider import CarouselDataProvider
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import CarouselFilter, RoleCriteriesGroup
from gui.Scaleform.daapi.view.meta.Comp7BattleTankCarouselMeta import Comp7BattleTankCarouselMeta
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.battle_control.gui_vehicle_builder import VehicleBuilder
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString as _ms
import nations
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if typing.TYPE_CHECKING:
    from gui.battle_control.arena_info.interfaces import IComp7PrebattleSetupController
_logger = logging.getLogger(__name__)
_FLAG_ICON_TEMPLATE = '../maps/icons/flags/160x100/%s.png'
_FLAG_SMALL_ICON_TEMPLATE = '../maps/icons/nations/155x31/%s.png'
_TYPE_ICON_TEMPLATE = '../maps/icons/vehicleTypes/big/%s.png'
_TYPE_ICON_SMALL_TEMPLATE = '../maps/icons/vehicleTypes/60x54/%s.png'

class _InBattleRentedCriteriesGroup(RoleCriteriesGroup):

    def __init__(self, rentedList):
        super(_InBattleRentedCriteriesGroup, self).__init__()
        self.__rentedList = rentedList

    def update(self, filters):
        self._criteria = REQ_CRITERIA.EMPTY
        self._setNationsCriteria(filters)
        self._setClassesCriteria(filters)
        self._setRentedCriteria(filters)
        self._setFavoriteVehicleCriteria(filters)
        self._setVehicleNameCriteria(filters)
        self._setRolesCriteria(filters)

    def _setRentedCriteria(self, filters):
        if not filters['rented']:
            self._criteria |= ~REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(self.__rentedList)


class _PrebattleCarouselFilter(CarouselFilter):

    def __init__(self):
        self.__rentedList = []
        super(_PrebattleCarouselFilter, self).__init__()
        self._serverSections = (COMP7_CAROUSEL_FILTER_1, COMP7_CAROUSEL_FILTER_2)
        self._clientSections = (COMP7_CAROUSEL_FILTER_CLIENT_1,)

    def save(self):
        pass

    def load(self):
        filters = AccountSettings.getFilterDefaults(self._serverSections)
        for section in self._clientSections:
            filters.update(AccountSettings.getFilterDefault(section))

        self._filters = filters
        self.update(filters, save=False)

    def setRentedList(self, rentedList):
        self.__rentedList = rentedList
        self._setCriteriaGroups()
        self._updateCriteriesGroups()

    def _setCriteriaGroups(self):
        self._criteriesGroups = (_InBattleRentedCriteriesGroup(self.__rentedList), RoleCriteriesGroup())


def getComp7CarouselVehicleDataVO(vehicle):
    return {'vehicleName': vehicle.shortUserName,
     'flagIcon': _FLAG_ICON_TEMPLATE % nations.NAMES[vehicle.nationID],
     'flagIconSmall': _FLAG_SMALL_ICON_TEMPLATE % nations.NAMES[vehicle.nationID],
     'vehicleIcon': vehicle.icon,
     'vehicleIconSmall': vehicle.iconSmall,
     'vehicleTypeIcon': _TYPE_ICON_TEMPLATE % vehicle.type,
     'vehicleTypeIconSmall': _TYPE_ICON_SMALL_TEMPLATE % vehicle.type,
     'favorite': vehicle.isFavorite,
     'enabled': True,
     'roleName': vehicle.roleLabel if vehicle.roleLabel != 'role_SPG' else ''}


class _PrebattleCarouselDataProvider(CarouselDataProvider):
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)
    _RawVehicleData = namedtuple('_RawVehicleData', ('strCD', 'settings', 'isElite', 'isRented'))

    def __init__(self, carouselFilter, itemsCache):
        super(_PrebattleCarouselDataProvider, self).__init__(carouselFilter, itemsCache)
        self.__vehiclesData = {}
        self.__selectedCD = None
        return

    def getSelectedCD(self):
        return self.__selectedCD

    def applyFilter(self, forceApply=False):
        prevFilteredIndices = self._filteredIndices[:]
        prevSelectedIdx = self._selectedIdx
        self._filteredIndices = []
        self._selectedIdx = -1
        visibleVehiclesIntCDs = [ vehicle.intCD for vehicle in self._getCurrentVehicles() ]
        for idx in self._getSortedIndices():
            if idx >= len(self._vehicles):
                _logger.debug('Could not find vehicle to apply filter')
                continue
            vehicle = self._vehicles[idx]
            if vehicle.intCD in visibleVehiclesIntCDs:
                self._filteredIndices.append(idx)
                if self.__selectedCD == vehicle.intCD:
                    self._selectedIdx = len(self._filteredIndices) - 1

        needUpdate = forceApply or prevFilteredIndices != self._filteredIndices or prevSelectedIdx != self._selectedIdx
        if needUpdate:
            self._filterByIndices()

    def getVehicleCDByIdx(self, filteredIdx):
        realIdx = self._filteredIndices[filteredIdx]
        vehicle = self._vehicles[realIdx]
        return vehicle.intCD

    def setVehicles(self, vehiclesList):
        self.__vehiclesData = {}
        rentedList = []
        for v in vehiclesList:
            vehData = self._RawVehicleData(v['compDescr'], v['settings'], bool(v['isElite']), bool(v['isRent']))
            intCD = vehicles.getVehicleType(vehData.strCD).compactDescr
            self.__vehiclesData[intCD] = vehData
            if vehData.isRented:
                rentedList.append(intCD)

        self._filter.setRentedList(rentedList)
        self.buildList()

    def setCurrentVehicle(self, vehicleCD):
        if vehicleCD is None:
            return
        else:
            for vehicle in self._vehicles:
                if vehicle.compactDescr == vehicleCD:
                    self.__selectedCD = vehicleCD
                    self.applyFilter()
                    self.refresh()
                    break

            return

    def _buildVehicleItems(self):
        self._vehicles = []
        self._vehicleItems = []
        vehicleIcons = []
        for vehicleData in self.__vehiclesData.itervalues():
            vehicle = self.__makeGuiVehicle(vehicleData)
            vehicleIcons.append(vehicle.icon)
            self._vehicles.append(vehicle)
            self._vehicleItems.append(getComp7CarouselVehicleDataVO(vehicle))

        self.app.imageManager.loadImages(vehicleIcons)

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (not vehicle.isFavorite,
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.userName)

    @staticmethod
    def __makeGuiVehicle(vehicleData):
        builder = VehicleBuilder()
        builder.setStrCD(vehicleData.strCD)
        builder.setSettings(vehicleData.settings)
        return builder.getResult()


class PrebattleTankCarousel(Comp7BattleTankCarouselMeta, IAbstractPeriodView):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(PrebattleTankCarousel, self).__init__()
        self._carouselDPCls = _PrebattleCarouselDataProvider
        self._carouselFilterCls = _PrebattleCarouselFilter
        self.__cooldownCallback = None
        return

    def hasRoles(self):
        return True

    def setFilter(self, idx):
        self.filter.switch(self._usedFilters[idx])
        self.blinkCounter()
        self.applyFilter()

    def setRowCount(self, value):
        self.as_rowCountS(value)

    def onViewIsHidden(self):
        self.destroy()

    def selectVehicle(self, idx):
        if self.__isSelectionInCooldown():
            return
        vehCD = self._carouselDP.getVehicleCDByIdx(idx)
        self.__getPRBController().chooseVehicle(vehCD)
        self.__startCooldown()

    def setPeriod(self, period):
        self.as_setEnabledS(period == ARENA_PERIOD.PREBATTLE)

    def _populate(self):
        super(PrebattleTankCarousel, self)._populate()
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self.as_initCarouselFilterS(self.__getInitialFilterVO(getFilterSetupContexts(1)))
        prebattleCtrl = self.__getPRBController()
        if prebattleCtrl is not None:
            prebattleCtrl.onVehiclesListUpdated += self.__onAvailableVehiclesUpdated
            prebattleCtrl.onVehicleChanged += self.__onSelectedVehicleChanged
            prebattleCtrl.onSelectionConfirmed += self.__onSelectionConfirmed
            prebattleCtrl.onBattleStarted += self.__onBattleStarted
            self._carouselDP.setVehicles(prebattleCtrl.getVehiclesList())
            currVehicle = prebattleCtrl.getCurrentVehicleInfo()
            if currVehicle:
                self._carouselDP.setCurrentVehicle(currVehicle['compDescr'])
        savedRowValue, isSavedByPlayer = getSavedRowCountValue()
        if isSavedByPlayer:
            self.as_rowCountS(rowValueToRowCount(savedRowValue))
        periodCtrl = self.__sessionProvider.shared.arenaPeriod
        self.as_setEnabledS(periodCtrl is not None and periodCtrl.getPeriod() == ARENA_PERIOD.PREBATTLE)
        return

    def _dispose(self):
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        prebattleCtrl = self.__getPRBController()
        if prebattleCtrl is not None:
            prebattleCtrl.onVehiclesListUpdated -= self.__onAvailableVehiclesUpdated
            prebattleCtrl.onVehicleChanged -= self.__onSelectedVehicleChanged
            prebattleCtrl.onSelectionConfirmed -= self.__onSelectionConfirmed
            prebattleCtrl.onBattleStarted -= self.__onBattleStarted
        self.__resetCooldown()
        super(PrebattleTankCarousel, self)._dispose()
        return

    def _initDataProvider(self):
        self._carouselDP = self._carouselDPCls(self._carouselFilterCls(), None)
        return

    def _getFilters(self):
        pass

    def __isSelectionInCooldown(self):
        return self.__cooldownCallback is not None

    def __getPRBController(self):
        return self.__sessionProvider.dynamic.comp7PrebattleSetup

    def __getInitialFilterVO(self, contexts):
        filters = self.filter.getFilters(self._usedFilters)
        hotFilters = []
        for entry in self._usedFilters:
            filterCtx = contexts.get(entry, FilterSetupContext())
            hotFilters.append({'id': entry,
             'value': getButtonsAssetPath(filterCtx.asset or entry),
             'selected': filters[entry],
             'enabled': True,
             'tooltip': makeTooltip('#tank_carousel_filter:tooltip/{}/header'.format(entry), _ms('#tank_carousel_filter:tooltip/{}/body'.format(entry), **filterCtx.ctx))})

        filtersVO = {'mainBtn': {'value': getButtonsAssetPath('params'),
                     'tooltip': '#comp7:battleCarousel/filterButtonTooltip'},
         'hotFilters': hotFilters,
         'isVisible': True}
        return filtersVO

    def __onViewLoaded(self, view, *args):
        if view.settings.alias == BATTLE_VIEW_ALIASES.COMP7_TANK_CAROUSEL_FILTER_POPOVER:
            view.setTankCarousel(self)

    def __onAvailableVehiclesUpdated(self, vehiclesList):
        self._carouselDP.setVehicles(vehiclesList)

    def __onSelectedVehicleChanged(self, vehicle):
        if vehicle:
            self._carouselDP.setCurrentVehicle(vehicle.intCD)

    def __onSelectionConfirmed(self):
        self.as_hideS(True)

    def __onBattleStarted(self):
        self.as_hideS(True)

    def __startCooldown(self):
        self.__resetCooldown()
        self.__cooldownCallback = BigWorld.callback(REQUEST_COOLDOWN.VEHICLE_IN_BATTLE_SWITCH, self.__onCooldownExpired)
        self.as_setEnabledS(False)

    def __onCooldownExpired(self):
        self.__resetCooldown()
        self.as_setEnabledS(True)

    def __resetCooldown(self):
        if self.__cooldownCallback is not None:
            BigWorld.cancelCallback(self.__cooldownCallback)
            self.__cooldownCallback = None
        return
