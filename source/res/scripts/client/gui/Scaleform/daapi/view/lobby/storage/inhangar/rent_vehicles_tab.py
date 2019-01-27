# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inhangar/rent_vehicles_tab.py
from CurrentVehicle import g_currentVehicle
from gui.Scaleform import MENU
from gui.Scaleform.daapi.view.lobby.storage.inhangar import StorageCarouselDataProvider, StorageCarouselFilter
from gui.Scaleform.daapi.view.meta.RentVehiclesTabViewMeta import RentVehiclesTabViewMeta
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import event_dispatcher as shared_events
from gui.shared.formatters.time_formatters import RentLeftFormatter
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers.i18n import makeString as _ms
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IRentalsController
from skeletons.gui.shared import IItemsCache

class _RentStorageCarouselFilter(StorageCarouselFilter):

    def __init__(self, criteries=None):
        super(_RentStorageCarouselFilter, self).__init__(criteries)
        self._clientSections = tuple()
        self._criteriesGroups = tuple()

    def save(self):
        pass


class _RentVehiclesDataProvider(StorageCarouselDataProvider):

    def __init__(self, carouselFilter, itemsCache, currentVehicle):
        super(_RentVehiclesDataProvider, self).__init__(carouselFilter, itemsCache, currentVehicle)
        self._baseCriteria = REQ_CRITERIA.VEHICLE.RENT | REQ_CRITERIA.INVENTORY

    def applyFilter(self):
        pass

    def _buildVehicle(self, item):
        vo = super(_RentVehiclesDataProvider, self)._buildVehicle(item)
        rentText = RentLeftFormatter(item.rentInfo, item.isPremiumIGR).getRentLeftStr() or _ms(MENU.STORE_VEHICLESTATES_RENTALISOVER)
        vo.update({'isMoneyEnough': True,
         'enabled': item.canSell and item.rentalIsOver,
         'rentText': rentText,
         'rentIcon': RES_ICONS.MAPS_ICONS_LIBRARY_CLOCKICON_1,
         'contextMenuId': CONTEXT_MENU_HANDLER_TYPE.STORAGE_VEHICLES_RENTED_ITEM})
        return vo


class RentVehiclesTabView(RentVehiclesTabViewMeta):
    _itemsCache = dependency.descriptor(IItemsCache)
    _rentalsCtrl = dependency.descriptor(IRentalsController)

    def _populate(self):
        super(RentVehiclesTabView, self)._populate()
        self._dataProvider.setEnvironment(self.app)
        self._itemsCache.onSyncCompleted += self.__onCacheResync
        self._rentalsCtrl.onRentChangeNotify += self.__updateVehicles
        self.__updateVehicles()

    def _dispose(self):
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        self._rentalsCtrl.onRentChangeNotify -= self.__updateVehicles
        super(RentVehiclesTabView, self)._dispose()

    def _getVO(self, item):
        pass

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.VEHICLE

    def removeItem(self, itemId):
        shared_events.showVehicleSellDialog(self._itemsCache.items.getItemByCD(int(itemId)).invID)

    def showItemInfo(self, itemId):
        shared_events.showVehicleInfo(itemId)

    def _buildItems(self):
        pass

    def _createDataProvider(self):
        return _RentVehiclesDataProvider(_RentStorageCarouselFilter(), self._itemsCache, g_currentVehicle)

    def __onCacheResync(self, reason, diff):
        forceUpdateReasons = (CACHE_SYNC_REASON.SHOP_RESYNC, CACHE_SYNC_REASON.DOSSIER_RESYNC, CACHE_SYNC_REASON.CLIENT_UPDATE)
        if reason in forceUpdateReasons:
            self.__updateVehicles()
        elif GUI_ITEM_TYPE.VEHICLE in diff:
            self.__updateVehicles(diff.get(GUI_ITEM_TYPE.VEHICLE))

    def __updateVehicles(self, vehicles=None, filterCriteria=None):
        self._dataProvider.updateVehicles(vehicles, filterCriteria)
        hasNoVehicles = self._dataProvider.getTotalVehiclesCount() == 0
        self.as_showDummyScreenS(hasNoVehicles)
