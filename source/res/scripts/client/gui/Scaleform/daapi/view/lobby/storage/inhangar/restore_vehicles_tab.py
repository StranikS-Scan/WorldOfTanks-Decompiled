# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inhangar/restore_vehicles_tab.py
from CurrentVehicle import g_currentVehicle
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import RestoreExchangeCreditsMeta
from gui.Scaleform.daapi.view.lobby.storage.inhangar import StorageCarouselDataProvider, StorageCarouselFilter
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleRestoreInfo, enoughCreditsForRestore
from gui.Scaleform.daapi.view.meta.RestoreVehiclesTabViewMeta import RestoreVehiclesTabViewMeta
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.shared import event_dispatcher as shared_events
from gui.shared.formatters import getItemPricesVO
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IRestoreController
from adisp import process

class _RestoreStorageCarouselFilter(StorageCarouselFilter):

    def __init__(self, criteries=None):
        super(_RestoreStorageCarouselFilter, self).__init__(criteries)
        self._clientSections = tuple()
        self._criteriesGroups = tuple()

    def save(self):
        pass


class _RestoreVehiclesDataProvider(StorageCarouselDataProvider):

    def __init__(self, carouselFilter, itemsCache, currentVehicle):
        super(_RestoreVehiclesDataProvider, self).__init__(carouselFilter, itemsCache, currentVehicle)
        self._baseCriteria = REQ_CRITERIA.VEHICLE.IS_RESTORE_POSSIBLE | ~REQ_CRITERIA.INVENTORY

    def applyFilter(self):
        pass

    def _buildVehicle(self, item):
        vo = super(_RestoreVehiclesDataProvider, self)._buildVehicle(item)
        restoreCreditsPrice = item.restorePrice.credits
        restorePrice = ItemPrice(item.restorePrice, item.restorePrice)
        enoughCredits, _ = enoughCreditsForRestore(restoreCreditsPrice, self._itemsCache)
        restoreAvailable, timerText, description, timerIcon = getVehicleRestoreInfo(item)
        vo.update({'price': getItemPricesVO(restorePrice)[0],
         'isMoneyEnough': enoughCredits,
         'enabled': enoughCredits and restoreAvailable,
         'description': description,
         'timerText': timerText,
         'timerIcon': timerIcon,
         'contextMenuId': CONTEXT_MENU_HANDLER_TYPE.STORAGE_VEHICLES_RESTORE_ITEM})
        return vo


class RestoreVehiclesTabView(RestoreVehiclesTabViewMeta):
    _restoreCtrl = dependency.descriptor(IRestoreController)

    def _populate(self):
        super(RestoreVehiclesTabView, self)._populate()
        self._dataProvider.setEnvironment(self.app)
        self._itemsCache.onSyncCompleted += self.__onCacheResync
        self._restoreCtrl.onRestoreChangeNotify += self.__updateVehicles
        self.__updateVehicles()

    def _dispose(self):
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        self._restoreCtrl.onRestoreChangeNotify -= self.__updateVehicles
        super(RestoreVehiclesTabView, self)._dispose()

    def _getVO(self, item):
        pass

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.VEHICLE

    @process
    def restoreItem(self, itemId):
        itemCD = int(itemId)
        item = self._itemsCache.items.getItemByCD(itemCD)
        restoreCreditsPrice = item.restorePrice.credits
        _, needGoldConversion = enoughCreditsForRestore(restoreCreditsPrice, self._itemsCache)
        if needGoldConversion:
            isOk, _ = yield DialogsInterface.showDialog(RestoreExchangeCreditsMeta(itemCD=itemCD))
            if not isOk:
                return
        shared_events.showVehicleBuyDialog(item)

    def showItemInfo(self, itemId):
        shared_events.showVehicleInfo(itemId)

    def _buildItems(self):
        pass

    def _createDataProvider(self):
        return _RestoreVehiclesDataProvider(_RestoreStorageCarouselFilter(), self._itemsCache, g_currentVehicle)

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
