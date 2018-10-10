# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inhangar/all_vehicles_tab.py
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_environment import formatCountString
from gui.Scaleform.daapi.view.lobby.storage.inhangar import StorageCarouselDataProvider, StorageCarouselFilter
from gui.Scaleform.daapi.view.meta.AllVehiclesTabViewMeta import AllVehiclesTabViewMeta
from gui.Scaleform.locale.TANK_CAROUSEL_FILTER import TANK_CAROUSEL_FILTER
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import CriteriesGroup
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IRentalsController, IIGRController
from gui.Scaleform.daapi.view.common.vehicle_carousel import carousel_environment
from CurrentVehicle import g_currentVehicle
from gui.shared.items_cache import CACHE_SYNC_REASON
_SEARCH_INPUT_MAX_CHARS = 50

class _CanSoldCriteriesGroup(CriteriesGroup):

    def update(self, filters):
        super(_CanSoldCriteriesGroup, self).update(filters)
        self._criteria |= ~REQ_CRITERIA.VEHICLE.CAN_NOT_BE_SOLD

    @staticmethod
    def isApplicableFor(vehicle):
        return vehicle.canNotBeSold


class _IsInInventoryCriteriesGroup(CriteriesGroup):

    def update(self, filters):
        super(_IsInInventoryCriteriesGroup, self).update(filters)
        self._criteria |= REQ_CRITERIA.INVENTORY

    @staticmethod
    def isApplicableFor(vehicle):
        return True


class AllVehiclesTabView(AllVehiclesTabViewMeta, carousel_environment.ICarouselEnvironment):
    rentals = dependency.descriptor(IRentalsController)
    igrCtrl = dependency.descriptor(IIGRController)

    @property
    def filter(self):
        return self._dataProvider.filter if self._dataProvider is not None else None

    def sellItem(self, itemId):
        shared_events.showVehicleSellDialog(self.itemsCache.items.getItemByCD(int(itemId)).invID)

    def showItemInfo(self, itemId):
        shared_events.showVehicleInfo(itemId)

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

    def blinkCounter(self):
        self.__updateCounter(True)

    def formatCountVehicles(self):
        return carousel_environment.formatCountString(self._dataProvider.getCurrentVehiclesCount(), self._dataProvider.getTotalVehiclesCount())

    def _populate(self):
        super(AllVehiclesTabView, self)._populate()
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

    def _dispose(self):
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        g_playerEvents.onVehicleBecomeElite -= self.__onVehicleBecomeElite
        g_prbCtrlEvents.onVehicleClientStateChanged -= self.__onVehicleClientStateChanged
        self.rentals.onRentChangeNotify -= self.__updateRent
        self.igrCtrl.onIgrTypeChanged -= self.__updateIgrType
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        super(AllVehiclesTabView, self)._dispose()

    def _getVO(self, item):
        pass

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.VEHICLE

    def _createDataProvider(self):
        return StorageCarouselDataProvider(StorageCarouselFilter((_CanSoldCriteriesGroup(), _IsInInventoryCriteriesGroup())), self.itemsCache, g_currentVehicle)

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
            self.__updateCounter(not self.filter.isDefault())
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
