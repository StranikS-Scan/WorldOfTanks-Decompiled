# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inhangar/all_vehicles_tab.py
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import CriteriesGroup
from gui.Scaleform.daapi.view.lobby.storage.inhangar import StorageCarouselDataProvider, StorageCarouselFilter
from gui.Scaleform.daapi.view.lobby.storage.storage_carousel_environment import StorageCarouselEnvironment
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import getVehicleUrl
from gui.Scaleform.daapi.view.meta.AllVehiclesTabViewMeta import AllVehiclesTabViewMeta
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IIGRController
from gui.shared.event_dispatcher import showWebShop

class _AllVehiclesTabCriteriesGroup(CriteriesGroup):

    def update(self, filters):
        super(_AllVehiclesTabCriteriesGroup, self).update(filters)
        self._criteria |= ~REQ_CRITERIA.VEHICLE.CAN_NOT_BE_SOLD | ~REQ_CRITERIA.VEHICLE.RENT

    @staticmethod
    def isApplicableFor(vehicle):
        return vehicle.canNotBeSold or vehicle.isRented


class AllVehiclesTabView(AllVehiclesTabViewMeta, StorageCarouselEnvironment):
    _igrCtrl = dependency.descriptor(IIGRController)

    def sellItem(self, itemId):
        shared_events.showVehicleSellDialog(self._itemsCache.items.getItemByCD(int(itemId)).invID)

    def navigateToStore(self):
        showWebShop(getVehicleUrl())

    def applyFilter(self):
        super(AllVehiclesTabView, self).applyFilter()
        self.__updateFilterWarning()

    def _populate(self):
        super(AllVehiclesTabView, self).setDataProvider(self._dataProvider)
        super(AllVehiclesTabView, self)._populate()
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self._dataProvider.setEnvironment(self.app)
        g_playerEvents.onVehicleBecomeElite += self.__onVehicleBecomeElite
        g_prbCtrlEvents.onVehicleClientStateChanged += self.__onVehicleClientStateChanged
        self._itemsCache.onSyncCompleted += self._onCacheResync
        self._igrCtrl.onIgrTypeChanged += self.__updateIgrType
        self.updateSearchInput(self.filter.get('searchNameVehicle'))
        self.__updateVehicles()

    def _dispose(self):
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        g_playerEvents.onVehicleBecomeElite -= self.__onVehicleBecomeElite
        g_prbCtrlEvents.onVehicleClientStateChanged -= self.__onVehicleClientStateChanged
        self._igrCtrl.onIgrTypeChanged -= self.__updateIgrType
        self._itemsCache.onSyncCompleted -= self._onCacheResync
        super(AllVehiclesTabView, self)._dispose()
        super(AllVehiclesTabView, self).clear()

    def _createDataProvider(self):
        return StorageCarouselDataProvider(StorageCarouselFilter((_AllVehiclesTabCriteriesGroup(),)), self._itemsCache, g_currentVehicle)

    def __onViewLoaded(self, view, *args, **kwargs):
        if view.settings is not None and view.settings.alias == VIEW_ALIAS.STORAGE_VEHICLES_FILTER_POPOVER:
            view.setTankCarousel(self)
        return

    def _onCacheResync(self, reason, diff):
        updateReasons = {CACHE_SYNC_REASON.CLIENT_UPDATE, CACHE_SYNC_REASON.SHOP_RESYNC, CACHE_SYNC_REASON.DOSSIER_RESYNC}
        if reason in updateReasons:
            self._dataProvider.buildList()
            self.__updateVehicles()
        elif GUI_ITEM_TYPE.VEHICLE in diff:
            self.__updateVehicles(diff.get(GUI_ITEM_TYPE.VEHICLE))

    def __updateVehicles(self, vehicles=None, filterCriteria=None):
        self._dataProvider.updateVehicles(vehicles, filterCriteria)
        self.updateCounter()
        self.__updateFilterWarning()
        hasNoVehicles = self._dataProvider.getTotalVehiclesCount() == 0
        self.as_showDummyScreenS(hasNoVehicles)

    def __updateIgrType(self, roomType, xpFactor):
        self.__updateVehicles(filterCriteria=REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR)

    def __updateFilterWarning(self):
        hasNoVehicles = self._dataProvider.getTotalVehiclesCount() == 0
        hasNoFilterResults = self._dataProvider.getCurrentVehiclesCount() == 0
        filterWarningVO = None
        if hasNoFilterResults and not hasNoVehicles:
            filterWarningVO = self._makeFilterWarningVO(STORAGE.FILTER_WARNINGMESSAGE, STORAGE.FILTER_NORESULTSBTN_LABEL, TOOLTIPS.STORAGE_FILTER_NORESULTSBTN)
        self.as_showFilterWarningS(filterWarningVO)
        return

    def __onVehicleBecomeElite(self, *vehicles):
        self.__updateVehicles(vehicles)

    def __onVehicleClientStateChanged(self, vehicles):
        self.__updateVehicles(vehicles)
