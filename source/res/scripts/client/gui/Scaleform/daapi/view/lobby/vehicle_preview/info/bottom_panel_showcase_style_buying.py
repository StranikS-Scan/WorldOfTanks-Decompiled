# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/bottom_panel_showcase_style_buying.py
import typing
from adisp import adisp_process
from gui import DialogsInterface
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID, I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsWebProductMeta
from gui.Scaleform.daapi.view.meta.VehiclePreviewBottomPanelShowcaseStyleBuyingMeta import VehiclePreviewBottomPanelShowcaseStyleBuyingMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.SystemMessages import SM_TYPE, pushI18nMessage
from gui.shared.event_dispatcher import mayObtainForMoney, mayObtainWithMoneyExchange
from gui.shared.formatters import formatPrice
from gui.shared.money import Currency, Money
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from gui.shop import showBuyGoldForBundle, showBuyProductOverlay
from helpers import dependency, time_utils
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, Optional, Union
    from gui.shared.gui_items.customization.c11n_items import Style
_ACTION_BTN_TOOLTIPS = R.strings.vehicle_preview.showcaseStyleBuying.actionBtn.tooltip

class _FinalizationNotifier(PeriodicNotifier):

    def __init__(self, deltaFunc, updateFunc):
        deltaFunc = self._wrapDeltaFunc(deltaFunc)
        super(_FinalizationNotifier, self).__init__(deltaFunc, updateFunc)

    def onFinalNotification(self):
        pass

    def _wrapDeltaFunc(self, deltaFunc):

        def _wrapper():
            delta = deltaFunc()
            if delta is None or delta <= 0:
                self.onFinalNotification()
            return delta

        return _wrapper


class VehiclePreviewBottomPanelShowcaseStyleBuying(VehiclePreviewBottomPanelShowcaseStyleBuyingMeta):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(VehiclePreviewBottomPanelShowcaseStyleBuying, self).__init__()
        self.__style = None
        self.__price = {}
        self.__endTime = 0
        self.__buyParams = None
        self.__originalPrice = {}
        self.__discountPercent = 0
        self.__notifier = _FinalizationNotifier(self.__getTimeDelta, self.__updateTimer)
        self.__notifier.onFinalNotification = self.__onTimeOver
        return

    def setData(self, style, price, endTime, originalPrice, buyParams, discountPercent):
        self.__style = style
        self.__price = price or {}
        self.__endTime = endTime or 0
        self.__buyParams = buyParams
        self.__originalPrice = originalPrice or {}
        self.__discountPercent = discountPercent or 0

    def update(self):
        isBought = not self.__price
        if isBought:
            self.as_setDataS({'isBought': True})
            return
        vPShowcaseStyleBuyingVO = self.__prepareVO()
        self.as_setDataS(vPShowcaseStyleBuyingVO)
        if self.__endTime:
            self.__notifier.startNotification()

    def _destroy(self):
        self.__notifier.stopNotification()
        self.__notifier.clear()
        self.__notifier = None
        super(VehiclePreviewBottomPanelShowcaseStyleBuying, self)._destroy()
        return

    def __prepareVO(self):
        priceMoney = Money(**self.__price)
        originalPriceMoney = Money(**self.__originalPrice)
        price = priceMoney.get(priceMoney.getCurrency()) or 0
        originalPrice = originalPriceMoney.get(originalPriceMoney.getCurrency()) or 0
        return {'originalPrice': originalPrice if originalPrice > price else 0,
         'price': price,
         'discountPercent': int(self.__discountPercent),
         'timeRemainingStr': '' if self.__endTime == 0 else self.__getTimeLeftStr(),
         'isBought': False,
         'priceType': priceMoney.getCurrency(),
         'isNoVehicle': not self.__haveSuitableVehicles,
         'actionBtnEnabled': self.__mayObtain(priceMoney),
         'actionBtnTooltip': self.__getActionBtnTooltip(priceMoney)}

    def onBuyClick(self):
        self.__onBuy()

    def __getActionBtnTooltip(self, priceMoney):
        if self.__endTime and self.__getTimeDelta() <= 0:
            return backport.text(_ACTION_BTN_TOOLTIPS.unavailable())
        return u'' if self.__mayObtain(priceMoney) else backport.text(_ACTION_BTN_TOOLTIPS.notEnoughFunds())

    @property
    def __haveSuitableVehicles(self):
        return bool(self.__itemsCache.items.getVehicles(criteria=REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.FOR_ITEM(self.__style)))

    @staticmethod
    def __mayObtain(priceMoney):
        return priceMoney.getCurrency() == Currency.GOLD or mayObtainForMoney(priceMoney) or mayObtainWithMoneyExchange(priceMoney)

    @adisp_process
    def __onBuy(self):
        productName = self.__style.userName
        money = Money(**self.__price)
        if not self.__mayObtain(money):
            pushI18nMessage(key=SYSTEM_MESSAGES.CUSTOMIZATION_CURRENCY_NOT_ENOUGH, type=SM_TYPE.Error)
            return
        if not mayObtainForMoney(money) and mayObtainWithMoneyExchange(money):
            isOk, _ = yield DialogsInterface.showDialog(ExchangeCreditsWebProductMeta(productName, 1, money.credits))
            if isOk:
                self.__onBuy()
                return
            return
        priceStr = formatPrice(money, reverse=True, useIcon=True)
        requestConfirmed = yield _buyRequestConfirmation(productName, priceStr)
        if requestConfirmed:
            if mayObtainForMoney(money):
                showBuyProductOverlay(self.__buyParams)
            elif money.gold > self.__itemsCache.items.stats.gold:
                showBuyGoldForBundle(money.gold, self.__buyParams)

    def __getTimeLeftStr(self):
        return time_utils.getTillTimeString(self.__getTimeDelta(), MENU.TIME_TIMEVALUESHORT)

    def __getTimeDelta(self):
        endTime = self.__endTime or 0
        return max(endTime - time_utils.getServerUTCTime(), 0)

    def __updateTimer(self):
        self.as_updateTimeRemainingS(self.__getTimeLeftStr())

    def __onTimeOver(self):
        vPShowcaseStyleBuyingVO = self.__prepareVO()
        self.as_setDataS(vPShowcaseStyleBuyingVO)
        self.as_setBuyingTimeElapsedS(True)


def _buyRequestConfirmation(productName, priceStr, key='buyConfirmation'):
    return DialogsInterface.showDialog(meta=I18nConfirmDialogMeta(key=key, messageCtx={'product': productName,
     'price': priceStr}, focusedID=DIALOG_BUTTON_ID.SUBMIT))
