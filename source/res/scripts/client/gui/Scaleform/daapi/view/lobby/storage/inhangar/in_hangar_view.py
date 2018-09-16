# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inhangar/in_hangar_view.py
from collections import namedtuple
import BigWorld
import nations
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import AccountSettings
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.common.filter_popover import VehiclesFilterPopover
from gui.Scaleform.daapi.view.common.vehicle_carousel import carousel_environment
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_data_provider import CarouselDataProvider
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_environment import formatCountString
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import CarouselFilter, CriteriesGroup, EventCriteriesGroup, BasicCriteriesGroup
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import createStorageDefVO, getBoosterType
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import getBuyVehiclesUrl, isIngameShopEnabled
from gui.Scaleform.daapi.view.meta.StorageCategoryInHangarViewMeta import StorageCategoryInHangarViewMeta
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.genConsts.STORE_TYPES import STORE_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.Scaleform.locale.TANK_CAROUSEL_FILTER import TANK_CAROUSEL_FILTER
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.shared import event_dispatcher as shared_events
from gui.shared.event_dispatcher import showWebShop, showOldShop
from gui.shared.formatters import getItemPricesVO, text_styles, icons
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import getTypeUserName, getVehicleStateIcon, Vehicle, VEHICLE_TYPES_ORDER_INDICES
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency, int2roman
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IIGRController, IRentalsController
StorageCategoryInHangarDataVO = namedtuple('StorageCategoryInHangarDataVO', ('displayString', 'isZeroCount', 'shouldShow', 'searchInputLabel', 'searchInputName', 'searchInputTooltip', 'searchInputMaxChars'))
_SEARCH_INPUT_MAX_CHARS = 50

class StorageVehicleFilterPopover(VehiclesFilterPopover):

    def _getInitialVO(self, filters, xpRateMultiplier):
        vo = super(StorageVehicleFilterPopover, self)._getInitialVO(filters, xpRateMultiplier)
        vo['searchSectionVisible'] = False
        return vo


class _CanSoldCriteriesGroup(CriteriesGroup):

    def update(self, filters):
        super(_CanSoldCriteriesGroup, self).update(filters)
        self._criteria |= ~REQ_CRITERIA.VEHICLE.CAN_NOT_BE_SOLD

    @staticmethod
    def isApplicableFor(vehicle):
        return vehicle.canNotBeSold


class _StorageFilter(CarouselFilter):

    def __init__(self):
        super(_StorageFilter, self).__init__()
        self._criteriesGroups = (_CanSoldCriteriesGroup(), EventCriteriesGroup(), BasicCriteriesGroup())

    def load(self):
        defaultFilters = AccountSettings.getFilterDefaults(self._serverSections)
        for section in self._clientSections:
            defaultFilters.update(AccountSettings.getFilterDefault(section))

        self._filters = defaultFilters
        self.update(defaultFilters, save=False)

    def save(self):
        pass


class _StorageCarouselDataProvider(CarouselDataProvider):

    def __init__(self, carouselFilter, itemsCache, currentVehicle):
        super(_StorageCarouselDataProvider, self).__init__(carouselFilter, itemsCache, currentVehicle)
        self._baseCriteria |= self.filter.criteria

    def buildList(self):
        self.clear()
        self.applyFilter()

    def applyFilter(self):
        self._buildVehicleItems()
        super(_StorageCarouselDataProvider, self).applyFilter()

    def _filterByIndices(self):
        self._vehicleItems = [ self._vehicleItems[ndx] for ndx in self._filteredIndices ]
        self.refresh()

    def _buildVehicle(self, item):
        name = _getVehicleName(vehicle=item)
        description = _getVehicleDescription(vehicle=item)
        stateIcon, stateText = _getVehicleInfo(vehicle=item)
        vo = createStorageDefVO(item.intCD, name, description, item.inventoryCount, getItemPricesVO(item.getSellPrice())[0], item.getShopIcon(STORE_CONSTANTS.ICON_SIZE_SMALL), item.getShopIcon(), RES_SHOP.getVehicleIcon(STORE_CONSTANTS.ICON_SIZE_SMALL, 'empty_tank'), itemType=getBoosterType(item), nationFlagIcon=RES_SHOP.getNationFlagIcon(nations.NAMES[item.nationID]), infoImgSrc=stateIcon, infoText=stateText)
        return vo

    def _getVehicleStats(self, vehicle):
        return {}

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (not vehicle.isInInventory,
         not vehicle.isEvent,
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.level,
         tuple(vehicle.buyPrices.itemPrice.price.iterallitems(byWeight=True)),
         vehicle.userName)


def _getVehicleName(vehicle):
    return ' '.join((getTypeUserName(vehicle.type, False), text_styles.neutral(int2roman(vehicle.level)), vehicle.shortUserName))


def _getVehicleDescription(vehicle):
    return ' '.join((_ms(STORAGE.CARD_VEHICLE_HOVER_MAXADDITIONALPRICELABEL), BigWorld.wg_getIntegralFormat(_calculateVehicleMaxAdditionalPrice(vehicle)), icons.credits()))


def _getVehicleInfo(vehicle):
    vState, vStateLvl = vehicle.getState()
    if vState not in Vehicle.CAN_SELL_STATES:
        infoTextStyle = text_styles.vehicleStatusCriticalText if vStateLvl == Vehicle.VEHICLE_STATE_LEVEL.CRITICAL else text_styles.vehicleStatusInfoText
        stateText = infoTextStyle(_ms(MENU.tankcarousel_vehiclestates(vState)))
        stateIcon = getVehicleStateIcon(vState)
        return (stateIcon, stateText)
    else:
        return (None, None)


def _calculateVehicleMaxAdditionalPrice(vehicle):
    items = list(vehicle.equipment.regularConsumables) + vehicle.optDevices + vehicle.shells
    return sum((item.getSellPrice().price.get(Currency.CREDITS, 0) * getattr(item, 'count', 1) for item in items if item is not None))


class StorageCategoryInHangarView(StorageCategoryInHangarViewMeta, carousel_environment.ICarouselEnvironment):
    rentals = dependency.descriptor(IRentalsController)
    igrCtrl = dependency.descriptor(IIGRController)

    def sellItem(self, itemId):
        shared_events.showVehicleSellDialog(self.itemsCache.items.getItemByCD(int(itemId)).invID)

    @property
    def filter(self):
        return self._dataProvider.filter if self._dataProvider is not None else None

    def navigateToStore(self):
        if isIngameShopEnabled():
            showWebShop(getBuyVehiclesUrl())
        else:
            showOldShop(ctx={'tabId': STORE_TYPES.SHOP,
             'component': STORE_CONSTANTS.VEHICLE})

    def changeSearchNameVehicle(self, inputText):
        self.filter.update({'searchNameVehicle': inputText}, save=False)
        self.applyFilter()

    def resetFilter(self):
        self.__updateSearchInput()
        self.filter.reset()
        self.applyFilter()

    def applyFilter(self):
        self._dataProvider.applyFilter()
        self.__updateCounter(not self.filter.isDefault())

    def showItemInfo(self, itemId):
        shared_events.showVehicleInfo(itemId)

    def blinkCounter(self):
        self.__updateCounter(True)

    def formatCountVehicles(self):
        return carousel_environment.formatCountString(self._dataProvider.getCurrentVehiclesCount(), self._dataProvider.getTotalVehiclesCount())

    def _createDataProvider(self):
        return _StorageCarouselDataProvider(_StorageFilter(), self.itemsCache, g_currentVehicle)

    def _populate(self):
        super(StorageCategoryInHangarView, self)._populate()
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self._dataProvider.setEnvironment(self.app)
        g_playerEvents.onVehicleBecomeElite += self.__onVehicleBecomeElite
        g_prbCtrlEvents.onVehicleClientStateChanged += self.__onVehicleClientStateChanged
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self.rentals.onRentChangeNotify += self.__updateRent
        self.igrCtrl.onIgrTypeChanged += self.__updateIgrType
        self.__currentFilteredVehicles = self._dataProvider.getCurrentVehiclesCount()
        self.__isFilterCounterShown = False
        self.__updateSearchInput()
        self.__updateVehicles()
        self.applyFilter()

    def _dispose(self):
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        g_playerEvents.onVehicleBecomeElite -= self.__onVehicleBecomeElite
        g_prbCtrlEvents.onVehicleClientStateChanged -= self.__onVehicleClientStateChanged
        self.rentals.onRentChangeNotify -= self.__updateRent
        self.igrCtrl.onIgrTypeChanged -= self.__updateIgrType
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        super(StorageCategoryInHangarView, self)._dispose()

    def _buildItems(self):
        pass

    def __updateSearchInput(self):
        searchInputTooltip = makeTooltip(TANK_CAROUSEL_FILTER.TOOLTIP_SEARCHINPUT_HEADER, _ms(TANK_CAROUSEL_FILTER.TOOLTIP_SEARCHINPUT_BODY, count=_SEARCH_INPUT_MAX_CHARS))
        searchInputLabel = _ms(TANK_CAROUSEL_FILTER.POPOVER_LABEL_SEARCHNAMEVEHICLE)
        self.as_updateSearchS(searchInputLabel, '', searchInputTooltip, _SEARCH_INPUT_MAX_CHARS)

    def __updateCounter(self, shouldShow):
        filteredVehicles = self._dataProvider.getCurrentVehiclesCount()
        totalVehicles = self._dataProvider.getTotalVehiclesCount()
        if filteredVehicles != totalVehicles and filteredVehicles != self.__currentFilteredVehicles:
            drawAttention = filteredVehicles == 0
            self.as_updateCounterS(shouldShow, formatCountString(filteredVehicles, totalVehicles), drawAttention)
            self.__currentFilteredVehicles = filteredVehicles
            self.__isFilterCounterShown = True
        if not shouldShow and self.__isFilterCounterShown:
            self.__currentFilteredVehicles = None
            self.__isFilterCounterShown = False
            self.as_updateCounterS(False, '', False)
        return

    def __onViewLoaded(self, view, *args, **kwargs):
        if view.settings.alias == VIEW_ALIAS.STORAGE_VEHICLES_FILTER_POPOVER:
            view.setTankCarousel(self)

    def __onCacheResync(self, reason, diff):
        if reason == CACHE_SYNC_REASON.CLIENT_UPDATE:
            self._dataProvider.buildList()
        elif reason in (CACHE_SYNC_REASON.SHOP_RESYNC, CACHE_SYNC_REASON.DOSSIER_RESYNC):
            self.__updateVehicles()
        elif GUI_ITEM_TYPE.VEHICLE in diff:
            self.__updateVehicles(diff.get(GUI_ITEM_TYPE.VEHICLE))

    def __updateVehicles(self, vehicles=None, filterCriteria=None):
        self._dataProvider.updateVehicles(vehicles, filterCriteria)
        self.applyFilter()
        hasNoVehicles = self._dataProvider.getTotalVehiclesCount() == 0
        self.as_showDummyScreenS(hasNoVehicles)

    def __updateRent(self, vehicles):
        self.__updateVehicles(vehicles)

    def __updateIgrType(self, roomType, xpFactor):
        self.__updateVehicles(filterCriteria=REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR)

    def __onVehicleBecomeElite(self, *vehicles):
        self.__updateVehicles(vehicles)

    def __onVehicleClientStateChanged(self, vehicles):
        self.__updateVehicles(vehicles)
