# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inhangar/restore_vehicles_tab.py
from CurrentVehicle import g_currentVehicle
from gui import DialogsInterface
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import CriteriesGroup
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import RestoreExchangeCreditsMeta
from gui.Scaleform.daapi.view.lobby.storage.inhangar import StorageCarouselDataProvider, StorageCarouselFilter
from gui.Scaleform.daapi.view.meta.RestoreVehiclesTabViewMeta import RestoreVehiclesTabViewMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency, i18n, time_utils
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.shared import IItemsCache
from adisp import process

def _enoughCreditsForRestore(restoreCreditsPrice, itemsCache):
    currentMoney = itemsCache.items.stats.money
    currentCredits = currentMoney.credits
    liquidityCredits = currentCredits + currentMoney.gold * itemsCache.items.shop.exchangeRate
    return (restoreCreditsPrice <= liquidityCredits, restoreCreditsPrice > currentCredits)


def _getVehicleRestoreInfo(vehicle):
    info = vehicle.restoreInfo
    if info.isInCooldown():
        enabled = False
        timeLeft = info.getRestoreCooldownTimeLeft()
        icon = RES_ICONS.MAPS_ICONS_LIBRARY_ICON_SAND_WATCH
        if timeLeft > time_utils.ONE_DAY:
            description = i18n.makeString(MENU.VEHICLE_RESTORECOOLDOWNLEFT_DAYS, time=int(timeLeft / time_utils.ONE_DAY))
        else:
            if timeLeft > time_utils.ONE_HOUR:
                timeValue = int(timeLeft / time_utils.ONE_HOUR)
            else:
                timeValue = '&lt;1'
            description = i18n.makeString(MENU.VEHICLE_RESTORECOOLDOWNLEFT_HOURS, time=timeValue)
    else:
        enabled = True
        timeLeft = 0 if info.isUnlimited() else info.getRestoreTimeLeft()
        description = i18n.makeString(STORAGE.CARD_VEHICLE_HOVER_RESTOREAVAILABLELABEL)
        icon = RES_ICONS.MAPS_ICONS_LIBRARY_CLOCKICON_1
    if timeLeft:
        timeStr = time_utils.getTillTimeString(timeLeft, MENU.TIME_TIMEVALUESHORT)
    else:
        timeStr = i18n.makeString(STORAGE.RESTORETIMELEFT_TIMELESS)
    return (enabled,
     timeStr,
     description,
     icon)


class _CanRestoreCriteriesGroup(CriteriesGroup):

    def update(self, filters):
        super(_CanRestoreCriteriesGroup, self).update(filters)
        self._criteria |= REQ_CRITERIA.VEHICLE.IS_RESTORE_POSSIBLE | ~REQ_CRITERIA.INVENTORY

    @staticmethod
    def isApplicableFor(vehicle):
        return True


class _RestoreVehiclesDataProvider(StorageCarouselDataProvider):

    def _buildVehicle(self, item):
        vo = super(_RestoreVehiclesDataProvider, self)._buildVehicle(item)
        restoreCreditsPrice = item.restorePrice.credits
        enoughCredits, _ = _enoughCreditsForRestore(restoreCreditsPrice, self._itemsCache)
        restoreAvailable, timerText, description, timerIcon = _getVehicleRestoreInfo(item)
        vo.update({'isMoneyEnough': enoughCredits,
         'enabled': enoughCredits and restoreAvailable,
         'description': description,
         'timerText': timerText,
         'timerIcon': timerIcon})
        return vo


class RestoreVehiclesTabView(RestoreVehiclesTabViewMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    restoreCtrl = dependency.descriptor(IRestoreController)

    def _populate(self):
        super(RestoreVehiclesTabView, self)._populate()
        self._dataProvider.setEnvironment(self.app)
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self.restoreCtrl.onRestoreChangeNotify += self.__updateVehicles
        self.__updateVehicles()

    def _dispose(self):
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        self.restoreCtrl.onRestoreChangeNotify -= self.__updateVehicles
        super(RestoreVehiclesTabView, self)._dispose()

    def _getVO(self, item):
        pass

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.VEHICLE

    @process
    def restoreItem(self, itemId):
        itemCD = int(itemId)
        item = self.itemsCache.items.getItemByCD(itemCD)
        restoreCreditsPrice = item.restorePrice.credits
        _, needGoldConversion = _enoughCreditsForRestore(restoreCreditsPrice, self.itemsCache)
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
        return _RestoreVehiclesDataProvider(StorageCarouselFilter((_CanRestoreCriteriesGroup(),)), self.itemsCache, g_currentVehicle)

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
