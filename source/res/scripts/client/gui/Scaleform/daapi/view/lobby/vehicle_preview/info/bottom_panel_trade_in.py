# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/bottom_panel_trade_in.py
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.VehiclePreviewBottomPanelTradeInMeta import VehiclePreviewBottomPanelTradeInMeta
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import event_dispatcher, events
from gui.shared.formatters import getItemPricesVO, text_styles
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.shared import IItemsCache
_RScopeTradeIn = R.strings.vehicle_preview.buyingPanel.tradeIn

class VehiclePreviewBottomPanelTradeIn(VehiclePreviewBottomPanelTradeInMeta):
    __tradeIn = dependency.descriptor(ITradeInController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(VehiclePreviewBottomPanelTradeIn, self).__init__()
        self.__tradeInVehicle = None
        self.__tradeOffVehicle = None
        self.__backAlias = None
        self.__backCallback = None
        return

    def onBuyClick(self):
        event_dispatcher.showVehicleBuyDialog(g_currentPreviewVehicle.item, previousAlias=VIEW_ALIAS.TRADE_IN_VEHICLE_PREVIEW, returnCallback=self.__backCallback, returnAlias=self.__backAlias)

    def setBackAlias(self, backAlias):
        self.__backAlias = backAlias

    def setBackCallback(self, backCallback):
        self.__backCallback = backCallback

    def _populate(self):
        super(VehiclePreviewBottomPanelTradeIn, self)._populate()
        self.__itemsCache.onSyncCompleted += self.__onCacheSyncCompleted
        self.addListener(events.VehicleBuyEvent.VEHICLE_SELECTED, self.__updateData)

    def _dispose(self):
        self.removeListener(events.VehicleBuyEvent.VEHICLE_SELECTED, self.__updateData)
        self.__itemsCache.onSyncCompleted -= self.__onCacheSyncCompleted
        super(VehiclePreviewBottomPanelTradeIn, self)._dispose()

    def _onRegisterFlashComponent(self, viewPy, alias):
        self.__updateData()
        if alias == VEHPREVIEW_CONSTANTS.TRADE_OFF_WIDGET_ALIAS:
            viewPy.setTradeInVehicle(self.__tradeInVehicle)

    def __updateData(self, _=None):
        self.__updateTradeVehicles()
        if self.__tradeInVehicle is not None:
            self.as_setDataS(self.__getVO())
        return

    def __getVO(self):
        statusText, statusOk, tradeOffAvailable = self.__getStatus()
        return {'currentPrice': getItemPricesVO(self.__tradeIn.getTradeInPrice(self.__tradeInVehicle)),
         'selectedPrice': self.__getSelectedPrice(),
         'statusText': statusText,
         'statusOk': statusOk,
         'tradeOffAvailable': tradeOffAvailable}

    def __updateTradeVehicles(self):
        self.__tradeInVehicle = g_currentPreviewVehicle.item
        self.__tradeOffVehicle = self.__tradeIn.getActiveTradeOffVehicle()

    def __getSelectedPrice(self):
        return None if self.__tradeOffVehicle is None else getItemPricesVO(ItemPrice(self.__tradeOffVehicle.tradeOffPrice, self.__tradeOffVehicle.tradeOffPrice))

    def __getStatus(self):
        if not self.__tradeIn.isEnabled():
            return (backport.text(_RScopeTradeIn.expired()), False, True)
        elif self.__tradeOffVehicle is not None and self.__tradeInVehicle is not None:
            tradeOffVehicles = self.__tradeIn.getTradeOffVehicles(self.__tradeInVehicle.level)
            isValidSelected = self.__tradeOffVehicle.intCD in tradeOffVehicles
            return (backport.text(_RScopeTradeIn.tradeOffPriceText() if isValidSelected else _RScopeTradeIn.invalidTradeOffVehicle()), isValidSelected, isValidSelected)
        elif self.__tradeIn.getTradeOffVehicles() and self.__tradeInVehicle is not None:
            levels = self.__tradeIn.getAllowedVehicleLevels(maxLevel=self.__tradeInVehicle.level)
            romanLevels = text_styles.neutral(toRomanRangeString(sequence=levels, rangeDelimiter=backport.text(R.strings.menu.rangeDelimiter())))
            return (backport.text(_RScopeTradeIn.availableLevels()).format(levels=romanLevels), True, True)
        else:
            return (backport.text(_RScopeTradeIn.notAvailableTradeOffVehicles()), False, True)

    def __onCacheSyncCompleted(self, updateReason, _=None):
        if updateReason in (CACHE_SYNC_REASON.SHOP_RESYNC, CACHE_SYNC_REASON.INVENTORY_RESYNC):
            self.__updateData()
