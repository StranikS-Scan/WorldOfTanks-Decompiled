# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/bottom_panel_showcase_style_buying.py
import typing
from gui.Scaleform.daapi.view.lobby.vehicle_preview.preview_bottom_panel_constants import ObtainingMethodInfo, ObtainingMethods, getShowcaseStyleObtainingInfo
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.meta.VehiclePreviewBottomPanelShowcaseStyleBuyingMeta import VehiclePreviewBottomPanelShowcaseStyleBuyingMeta
from gui.Scaleform.daapi.view.lobby.vehicle_preview.info import dyn_currencies_utils as dyn_utils
from gui.Scaleform.daapi.view.lobby.vehicle_preview.info.style_buying import StyleBuyingProcessor
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.SystemMessages import SM_TYPE, pushI18nMessage
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Dict, Optional, Union
    from gui.shared.money import Money
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
        self.__dynPrice = {}
        self.__endTime = 0
        self.__originalPrice = {}
        self.__originalDynPrice = {}
        self.__discountPercent = 0
        self.__obtainingInfo = getShowcaseStyleObtainingInfo(ObtainingMethods.BUY.value)
        if not self.__obtainingInfo:
            raise SoftException('obtainingMethod: %s is not supported' % ObtainingMethods.BUY.value)
        self.__notifier = _FinalizationNotifier(self.__getTimeDelta, self.__updateTimer)
        self.__notifier.onFinalNotification = self.__onTimeOver
        self.__buyingProcessor = StyleBuyingProcessor()
        return

    def setData(self, style, price, endTime, originalPrice, buyParams, discountPercent, obtainingMethod):
        self.__style = style
        self.__price, self.__dynPrice = dyn_utils.separatePrice(price or {})
        self.__endTime = endTime or 0
        self.__originalPrice, self.__originalDynPrice = dyn_utils.separatePrice(originalPrice or {})
        self.__discountPercent = discountPercent or 0
        self.__obtainingInfo = getShowcaseStyleObtainingInfo(obtainingMethod)
        if not self.__obtainingInfo:
            raise SoftException('obtainingMethod: %s is not supported' % obtainingMethod)
        self.__buyingProcessor.setStyle(self.__style)
        self.__buyingProcessor.setBuyParams(buyParams)
        self.__buyingProcessor.setConfiramtionKey(self.__obtainingInfo.confirmation_key)

    def update(self):
        isBought = not (self.__price or self.__dynPrice)
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
        priceMoney = dyn_utils.getMoney(self.__price, self.__dynPrice)
        originalPriceMoney = dyn_utils.getMoney(self.__originalPrice, self.__originalDynPrice)
        price = priceMoney.get(priceMoney.getCurrency()) or 0
        originalPrice = originalPriceMoney.get(originalPriceMoney.getCurrency()) or 0
        return {'originalPrice': originalPrice if originalPrice > price else 0,
         'price': price,
         'discountPercent': int(self.__discountPercent),
         'timeRemainingStr': '' if self.__endTime == 0 else self.__getTimeLeftStr(),
         'isBought': False,
         'priceType': priceMoney.getCurrency(),
         'isNoVehicle': not self.__haveSuitableVehicles,
         'actionBtnEnabled': self.__buyingProcessor.mayObtain(priceMoney),
         'actionBtnTooltip': self.__getActionBtnTooltip(priceMoney),
         'actionBtnLabel': self.__getActionBtnLabel()}

    def onBuyClick(self):
        self.__onBuy()

    def __getActionBtnTooltip(self, priceMoney):
        if self.__endTime and self.__getTimeDelta() <= 0:
            return backport.text(_ACTION_BTN_TOOLTIPS.unavailable())
        return u'' if self.__buyingProcessor.mayObtain(priceMoney) else backport.text(_ACTION_BTN_TOOLTIPS.notEnoughFunds())

    def __getActionBtnLabel(self):
        return backport.text(self.__obtainingInfo.btn_label)

    @property
    def __haveSuitableVehicles(self):
        return bool(self.__itemsCache.items.getVehicles(criteria=REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.FOR_ITEM(self.__style)))

    def __onBuy(self):
        money = dyn_utils.getMoney(self.__price, self.__dynPrice)
        if not self.__buyingProcessor.mayObtain(money):
            pushI18nMessage(key=SYSTEM_MESSAGES.CUSTOMIZATION_CURRENCY_NOT_ENOUGH, type=SM_TYPE.Error)
            return
        self.__buyingProcessor.buy(money)

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
