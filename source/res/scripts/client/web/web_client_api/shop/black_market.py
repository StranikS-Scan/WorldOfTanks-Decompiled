# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop/black_market.py
from enum import Enum
from functools import partial
import adisp
import async
from constants import LOOTBOX_TOKEN_PREFIX
from gui.impl.gen import R
from gui.impl.lobby.loot_box.loot_box_helper import getObtainableVehicles
from gui.shared.event_dispatcher import showBlackMarketOpenItemWindow, showBlackMarketVehicleListWindow, showShop, showCurrencyExchangeDialog
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.gui_items.loot_box import BLACK_MARKET_ITEM_TYPE
from gui.shared.gui_items.processors.market_items import MarketItemNextOpenRecordsProcessor
from gui.shared.money import Money
from helpers import dependency
from skeletons.gui.game_control import IEventItemsController
from web.web_client_api import w2c, W2CSchema, Field

class _ItemStatus(Enum):
    ITEM_CLOSED = 'itemClosed'
    ITEM_OPENED = 'itemOpened'


class _OpenVehicleListSchema(W2CSchema):
    back_url = Field(required=False, type=basestring)


class _OpenExchangeDialogSchema(W2CSchema):
    reason = Field(required=False, type=basestring, default='')
    product_name = Field(required=False, type=basestring, default='')
    products_amount = Field(required=False, type=int, default=0)
    price_type = Field(required=True, type=basestring)
    price = Field(required=True, type=int)


class BlackMarketWebApiMixin(W2CSchema):
    __eventItemsCtrl = dependency.descriptor(IEventItemsController)
    __EXCHANGE_REASON_TO_TITLE_RES_ID = {'simple': R.strings.bm2021.dialog.exchangeSimple.title(),
     'product': R.strings.bm2021.dialog.exchangeProduct.title(),
     'auction': R.strings.bm2021.dialog.exchangeAuction.title()}

    @w2c(_OpenExchangeDialogSchema, name='open_currency_exchange_window')
    def openCurrencyExchangeDialog(self, cmd):

        @adisp.async
        @async.async
        def proxy(price, titleResId, productName, productsAmount, callback):
            res = yield async.await(showCurrencyExchangeDialog(price, titleResId, productName, productsAmount))
            callback(res)

        moneyArgs = {cmd.price_type: cmd.price}
        result = yield proxy(ItemPrice(Money(**moneyArgs), Money(**moneyArgs)), self.__EXCHANGE_REASON_TO_TITLE_RES_ID.get(cmd.reason, R.strings.bm2021.dialog.exchangeGold.title()), cmd.product_name, cmd.products_amount)
        yield {'completed': not result.busy and result.result[0]}

    @w2c(_OpenVehicleListSchema, name='open_black_market_vehicle_list_window')
    def openVehicleListWindow(self, cmd):
        showBlackMarketVehicleListWindow(partial(self.__vehicleListRestoreCallback, cmd.back_url))

    @w2c(W2CSchema, name='open_black_market_item_window')
    def openBlackMarketItemWindow(self, _):
        showBlackMarketOpenItemWindow(soundSpace=None)
        return

    @w2c(W2CSchema, name='get_black_market_item_info')
    def getBlackMarketItemInfo(self, _):
        hasItem = False
        obtainableVehicles = 0
        itemStatus = _ItemStatus.ITEM_OPENED.value
        tokenID = ''
        wasOpened = False
        item = self.__eventItemsCtrl.getEventItemsByType(BLACK_MARKET_ITEM_TYPE)
        if item is not None:
            hasItem = item.getInventoryCount() > 0
            tokenID = LOOTBOX_TOKEN_PREFIX + str(item.getID())
            obtainableVehicles = len(getObtainableVehicles(item))
            result = yield MarketItemNextOpenRecordsProcessor().request()
            isItemClosed = result.success and not result.auxData.get('blackMarket', {}).get('rolledRewards', {})
            if hasItem and isItemClosed:
                itemStatus = _ItemStatus.ITEM_CLOSED.value
            wasOpened = result.success and result.auxData.get('blackMarket', {}).get('lastUpdate', 0) > 0
        yield {'hasItem': hasItem,
         'obtainableVehicles': obtainableVehicles,
         'itemStatus': itemStatus,
         'tokenID': tokenID,
         'wasOpened': wasOpened}
        return

    def __vehicleListRestoreCallback(self, url):
        showShop(url)
        showBlackMarketVehicleListWindow(partial(self.__vehicleListRestoreCallback, url))
