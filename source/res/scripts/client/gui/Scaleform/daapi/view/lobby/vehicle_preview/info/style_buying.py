# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/style_buying.py
import typing
from adisp import adisp_process
from gui import DialogsInterface
from gui.shared.formatters import formatPrice
from gui.shared.money import Money, Currency
from gui.shop import showBuyGoldForBundle, showBuyProductOverlay
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID, I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsWebProductMeta
from gui.Scaleform.daapi.view.lobby.vehicle_preview.info import dyn_currencies_utils as dyn_utils
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, Union

class StyleBuyingProcessor(object):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, confirmationKey='buyConfirmation'):
        super(StyleBuyingProcessor, self).__init__()
        self.__buyParams = None
        self.__confirmationKey = confirmationKey
        self.__style = None
        return

    def setConfiramtionKey(self, confirmationKey):
        self.__confirmationKey = confirmationKey

    def setStyle(self, style):
        self.__style = style

    def setBuyParams(self, buyParams):
        self.__buyParams = buyParams

    def mayObtain(self, price):
        currency = price.getCurrency()
        return currency == Currency.GOLD or dyn_utils.mayObtainForMoney(price) or dyn_utils.mayObtainWithMoneyExchange(price)

    @adisp_process
    def buy(self, price):
        if self.__buyParams is not None and self.__style:
            if not dyn_utils.mayObtainForMoney(price) and dyn_utils.mayObtainWithMoneyExchange(price):
                isOk, _ = yield DialogsInterface.showDialog(ExchangeCreditsWebProductMeta(self.__style.userName, 1, price.credits))
                if not isOk:
                    return
            self.__buy(price)
        else:
            raise SoftException('buyParams and style attributes are expected to be not None')
        return

    @adisp_process
    def __buy(self, money):
        priceStr = formatPrice(money, currency=money.getCurrency(), reverse=True, useIcon=True)
        requestConfirmed = yield _buyRequestConfirmation(self.__style.userName, priceStr, self.__confirmationKey)
        if requestConfirmed:
            if dyn_utils.isMoney(money):
                self.__obtainByOrdinaryCurrency(money)
            else:
                self.__obtainByDynamicCurrency(money)

    def __obtainByOrdinaryCurrency(self, money):
        if dyn_utils.mayObtainForMoney(money):
            showBuyProductOverlay(self.__buyParams)
        elif money.gold > self.__itemsCache.items.stats.gold:
            showBuyGoldForBundle(money.gold, self.__buyParams)

    def __obtainByDynamicCurrency(self, money):
        method = dyn_utils.getBuyProductMethod(money)
        if not method:
            raise SoftException("Can't find buy method for dyn currency: {}".format(money.getCurrency()))
        if dyn_utils.mayObtainForMoney(money):
            method(self.__buyParams)


def _buyRequestConfirmation(productName, priceStr, key):
    return DialogsInterface.showDialog(meta=I18nConfirmDialogMeta(key=key, messageCtx={'product': productName,
     'price': priceStr}, focusedID=DIALOG_BUTTON_ID.SUBMIT))
