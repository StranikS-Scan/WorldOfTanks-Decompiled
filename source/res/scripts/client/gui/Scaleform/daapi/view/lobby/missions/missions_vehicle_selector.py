# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/missions_vehicle_selector.py
import Event
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import AccountSettings, SELECTOR_FILTER_1
from gui.Scaleform import getButtonsAssetPath
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehicle_carousel.carousel_data_provider import CarouselDataProvider, getVehicleDataVO, getStatusStrings
from gui.Scaleform.daapi.view.lobby.vehicle_carousel.carousel_filter import CarouselFilter, BasicCriteriesGroup, EventCriteriesGroup
from gui.Scaleform.daapi.view.meta.MissionsVehicleSelectorMeta import MissionsVehicleSelectorMeta
from gui.Scaleform.daapi.view.meta.VehicleSelectorCarouselMeta import VehicleSelectorCarouselMeta
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events import caches
from gui.shared.formatters import text_styles
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers.i18n import makeString as ms

class SelectorCriteriesGroup(BasicCriteriesGroup):
    """ Criteria group used in missions vehicle selector.
    
    The only difference is an extra inventory criteria.
    """

    def update(self, filters):
        super(SelectorCriteriesGroup, self).update(filters)
        if filters['inventory']:
            self._criteria |= REQ_CRITERIA.INVENTORY


class _MissionsCarouselFilter(CarouselFilter):
    """ Carousel filter for missions vehicle selector.
    
    This filter utilizes same sections as hangar carousel, but has specific
    saving and loading rules.
    """

    def __init__(self):
        super(_MissionsCarouselFilter, self).__init__()
        self._serverSections += (SELECTOR_FILTER_1,)
        self._criteriesGroups = (EventCriteriesGroup(), SelectorCriteriesGroup())

    def load(self):
        filters = AccountSettings.getFilterDefaults(self._serverSections)
        for section in self._clientSections:
            filters.update(AccountSettings.getFilterDefault(section))

        filters.update(caches.getNavInfo().getVehicleSelectorFilters())
        self._filters = filters
        self.update(filters, save=False)

    def save(self):
        filters = AccountSettings.getFilterDefault(SELECTOR_FILTER_1)
        filters = {key:value for key, value in self._filters.iteritems() if key in filters}
        caches.getNavInfo().setVehicleSelectorFilters(filters)


class _MissionsCarouselDataProvider(CarouselDataProvider):
    """ Carousel data provider for missions vehicle selector.
    """

    def __init__(self, carouselFilter, itemsCache, currentVehicle):
        super(_MissionsCarouselDataProvider, self).__init__(carouselFilter, itemsCache, currentVehicle)
        self.__suitableVehiclesIDs = []
        self.__extraConditions = []

    def setCriteria(self, criteria, extraConditions):
        self._baseCriteria = criteria
        self.__extraConditions = extraConditions
        self._filter.reset(exceptions=('inventory',))

    def getSuitableVehicles(self):
        return self.__suitableVehiclesIDs

    def getSuitableVehiclesCount(self):
        return len(self.__suitableVehiclesIDs)

    def _dispose(self):
        self.__extraConditions = []
        super(_MissionsCarouselDataProvider, self)._dispose()

    def _buildVehicleItems(self):
        self.__suitableVehiclesIDs = []
        super(_MissionsCarouselDataProvider, self)._buildVehicleItems()

    def _buildVehicle(self, vehicle):
        vehicleVO = super(_MissionsCarouselDataProvider, self)._buildVehicle(vehicle)
        vehicleVO.update(isUseRightBtn=False)
        xpFactor = self._itemsCache.items.shop.dailyXPFactor
        if vehicle.isInInventory:
            for condition in self.__extraConditions:
                isOk, reason = condition.isAvailableReason(vehicle)
                if not isOk:
                    smallStatus, largeStatus = getStatusStrings(reason, ctx={'factor': xpFactor})
                    vehicleVO.update(smallInfoText=smallStatus, infoText=largeStatus, lockBackground=True, clickEnabled=False, infoImgSrc='', isCritInfo=False)
                    break
            else:
                self.__suitableVehiclesIDs.append(vehicle.intCD)

        return vehicleVO


class VehicleSelectorCarousel(VehicleSelectorCarouselMeta):
    """ Carousel for displaying suitable vehicles for a quest.
    """

    def __init__(self):
        super(VehicleSelectorCarousel, self).__init__()
        self._usedFilters = ('inventory',)
        self._carouselDPCls = _MissionsCarouselDataProvider
        self._carouselFilterCls = _MissionsCarouselFilter

    def setFilter(self, idx):
        self.filter.switch(self._usedFilters[idx])
        self.applyFilter()

    def getSuitableVehicles(self):
        return self._carouselDP.getSuitableVehicles()

    def getSuitableVehiclesCount(self):
        return self._carouselDP.getSuitableVehiclesCount()

    def setCriteria(self, criteria, extraConditions):
        self._carouselDP.setCriteria(criteria, extraConditions)
        self.updateVehicles()

    def _populate(self):
        super(VehicleSelectorCarousel, self)._populate()
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        filters = self.filter.getFilters(self._usedFilters)
        self.as_initCarouselFilterS({'mainBtn': {'value': getButtonsAssetPath('params'),
                     'tooltip': '#tank_carousel_filter:tooltip/params'},
         'hotFilters': [{'value': QUESTS.QUESTS_TABLE_INHANGAR,
                         'tooltip': '#tank_carousel_filter:tooltip/inventory',
                         'selected': filters['inventory']}]})

    def _dispose(self):
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        super(VehicleSelectorCarousel, self)._dispose()

    def __onViewLoaded(self, view):
        if view.settings.alias == VIEW_ALIAS.VEHICLES_FILTER_POPOVER:
            view.setTankCarousel(self)


class MissionsVehicleSelector(MissionsVehicleSelectorMeta):
    """ Vehicle selector for a quest.
    
    Vehicle selector is used to select vehicle among suitable for the quest
    (based on vehicle requirements section in quest).
    """

    def __init__(self):
        super(MissionsVehicleSelector, self).__init__()
        self.__carousel = None
        return

    def setCriteria(self, criteria, extraConditions):
        self.__carousel.setCriteria(criteria, extraConditions)
        self.__updateSelectedVehicle()

    def _populate(self):
        super(MissionsVehicleSelector, self)._populate()
        g_currentVehicle.onChanged += self.__selectVehicle
        self.__carousel = self.components.get(QUESTS_ALIASES.VEHICLE_SELECTOR_CAROUSEL_ALIAS)
        self.__updateSelectedVehicle()

    def _dispose(self):
        g_currentVehicle.onChanged -= self.__selectVehicle
        self.__carousel = None
        super(MissionsVehicleSelector, self)._dispose()
        return

    def __selectVehicle(self):
        self.__updateSelectedVehicle()
        self.as_closeS()

    def __updateSelectedVehicle(self):
        vehicle = g_currentVehicle.item
        suitableVehicles = self.__carousel.getSuitableVehicles()
        if suitableVehicles and vehicle and vehicle.intCD in suitableVehicles:
            selectedVeh = getVehicleDataVO(vehicle)
            selectedVeh.update({'tooltip': TOOLTIPS.MISSIONS_VEHICLE_SELECTOR_LIST})
            status = text_styles.statInfo(QUESTS.MISSIONS_VEHICLESELECTOR_STATUS_SELECTED)
        elif suitableVehicles:
            label = QUESTS.MISSIONS_VEHICLESELECTOR_STATUS_SELECT
            style = text_styles.premiumVehicleName
            selectedVeh = {'buyTank': True,
             'iconSmall': RES_ICONS.MAPS_ICONS_LIBRARY_EMPTY_SELECTION,
             'smallInfoText': style(label),
             'tooltip': TOOLTIPS.MISSIONS_VEHICLE_SELECTOR_SELECT}
            status = ''
        else:
            label = QUESTS.MISSIONS_VEHICLESELECTOR_STATUS_LIST
            style = text_styles.premiumVehicleName
            selectedVeh = {'buyTank': True,
             'iconSmall': RES_ICONS.MAPS_ICONS_LIBRARY_EMPTY_SELECTION,
             'smallInfoText': style(label),
             'tooltip': TOOLTIPS.MISSIONS_VEHICLE_SELECTOR_LIST}
            status = text_styles.critical(QUESTS.MISSIONS_VEHICLESELECTOR_STATUS_NOTAVAILABLE)
        selectedVeh.update(isUseRightBtn=False)
        suitableVehiclesCount = self.__carousel.getSuitableVehiclesCount()
        totalVehiclesCount = self.__carousel.getTotalVehiclesCount()
        if suitableVehiclesCount == 0:
            suitableStyle = text_styles.unavailable
        else:
            suitableStyle = text_styles.highTitle
        count = '{} / {}'.format(suitableStyle(suitableVehiclesCount), text_styles.main(totalVehiclesCount))
        title = text_styles.highTitle(ms(QUESTS.MISSIONS_VEHICLESELECTOR_TITLE, count=count))
        self.as_setInitDataS({'title': title,
         'statusText': status})
        self.as_showSelectedVehicleS(selectedVeh)
