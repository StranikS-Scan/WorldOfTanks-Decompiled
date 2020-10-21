# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/vehicle_preview_personal_trade_in_buying_panel.py
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.VehiclePreviewTradeInBuyingPanelMeta import VehiclePreviewTradeInBuyingPanelMeta
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import event_dispatcher, events
from gui.shared.formatters import getItemPricesVO, text_styles
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.gui.game_control import IPersonalTradeInController
from skeletons.gui.shared import IItemsCache
_RScopeTradeIn = R.strings.vehicle_preview.buyingPanel.tradeIn

class VehiclePreviewPersonalTradeInBuyingPanel(VehiclePreviewTradeInBuyingPanelMeta):
    __personalTradeIn = dependency.descriptor(IPersonalTradeInController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(VehiclePreviewPersonalTradeInBuyingPanel, self).__init__()
        self.__personalTradeInBuyVehicle = self.__personalTradeIn.getActiveTradeInBuyVehicle()
        self.__personalTradeInSaleVehicle = self.__personalTradeIn.getActiveTradeInSaleVehicle()

    def onBuyClick(self):
        event_dispatcher.showVehicleBuyDialog(g_currentPreviewVehicle.item, previousAlias=VIEW_ALIAS.PERSONAL_TRADE_IN_VEHICLE_PREVIEW, returnCallback=event_dispatcher.showHangar)

    def _populate(self):
        super(VehiclePreviewPersonalTradeInBuyingPanel, self)._populate()
        self.__itemsCache.onSyncCompleted += self.__onCacheSyncCompleted
        self.__personalTradeIn.onActiveSaleVehicleChanged += self.__updateData
        self.addListener(events.VehicleBuyEvent.VEHICLE_SELECTED, self.__updateData)
        self.__personalTradeInBuyVehicle = self.__personalTradeIn.getActiveTradeInBuyVehicle()
        self.__personalTradeInSaleVehicle = self.__personalTradeIn.getActiveTradeInSaleVehicle()

    def _dispose(self):
        self.removeListener(events.VehicleBuyEvent.VEHICLE_SELECTED, self.__updateData)
        self.__itemsCache.onSyncCompleted -= self.__onCacheSyncCompleted
        self.__personalTradeIn.onActiveSaleVehicleChanged -= self.__updateData
        super(VehiclePreviewPersonalTradeInBuyingPanel, self)._dispose()

    def _onRegisterFlashComponent(self, viewPy, alias):
        self.__updateData()
        if alias == VEHPREVIEW_CONSTANTS.TRADE_OFF_WIDGET_ALIAS:
            viewPy.setTradeInVehicle(self.__personalTradeInBuyVehicle)

    def __updateData(self, _=None):
        self.__updateTradeVehicles()
        if self.__personalTradeInBuyVehicle is None or self.__personalTradeInSaleVehicle is None or self.__personalTradeInBuyVehicle.intCD not in self.__personalTradeIn.getBuyVehicleCDs() or self.__personalTradeInSaleVehicle.intCD not in self.__personalTradeIn.getSaleVehicleCDs():
            event_dispatcher.showHangar()
        else:
            self.as_setDataS(self.__getVO())
        return

    def __getVO(self):
        shortName = self.__personalTradeIn.getActiveTradeInBuyVehicle().shortUserName
        itemPrice = self.__personalTradeIn.getPersonalTradeInPrice(self.__personalTradeInBuyVehicle)
        statusText, isFreeExchange = self.__getStatus(itemPrice)
        currentPrice = [{'defPrice': (('gold', itemPrice.defPrice.gold),),
          'price': (('gold', itemPrice.price.gold),)}]
        return {'currentPrice': currentPrice,
         'selectedPrice': self.__getSelectedPrice(itemPrice),
         'statusText': statusText,
         'statusOk': True,
         'tradeOffAvailable': True,
         'isFreeExchange': isFreeExchange,
         'title': backport.text(R.strings.vehicle_preview.buyingPanel.personalTradeIn.title(), name=shortName)}

    def __updateTradeVehicles(self):
        self.__personalTradeInBuyVehicle = g_currentPreviewVehicle.item
        self.__personalTradeInSaleVehicle = self.__personalTradeIn.getActiveTradeInSaleVehicle()

    def __getSelectedPrice(self, itemPrice):
        if self.__personalTradeInSaleVehicle is None:
            return
        else:
            price = itemPrice.defPrice - itemPrice.price
            return getItemPricesVO(ItemPrice(price, price))

    def __onCacheSyncCompleted(self, updateReason, _=None):
        if updateReason in (CACHE_SYNC_REASON.SHOP_RESYNC, CACHE_SYNC_REASON.INVENTORY_RESYNC):
            self.__updateData()

    def __getStatus(self, itemPrice):
        if itemPrice.price.gold == 0:
            statusText = text_styles.statInfo(backport.text(_RScopeTradeIn.personaltradeOffPriceText()))
            isFreeExchange = True
        else:
            statusText = backport.text(_RScopeTradeIn.tradeOffPriceText())
            isFreeExchange = False
        return (statusText, isFreeExchange)
