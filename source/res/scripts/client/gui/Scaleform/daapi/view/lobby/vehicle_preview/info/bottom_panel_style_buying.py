# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/bottom_panel_style_buying.py
import typing
from CurrentVehicle import g_currentPreviewVehicle
from adisp import process
from battle_pass_common import CurrencyBP
from frameworks.wulf import ViewFlags, ViewSettings
from gui import DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID, I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsWebProductMeta
from gui.Scaleform.daapi.view.meta.VehiclePreviewBottomPanelStyleBuyingMeta import VehiclePreviewBottomPanelStyleBuyingMeta
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_preview.buying_panel.style_buying_panel_model import StyleBuyingPanelModel, StyleBuyingStatus
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import mayObtainForMoney, mayObtainWithMoneyExchange
from gui.shared.formatters import formatPrice
from gui.shared.money import Currency, Money
from gui.shop import showBuyGoldForBundle, showBuyProductOverlay
from helpers import dependency
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
if typing.TYPE_CHECKING:
    from typing import Dict, Optional, Tuple
    from gui.shared.gui_items.customization.c11n_items import Style
_BUY_PRODUCT_USING_DYN = {CurrencyBP.BIT.value: showBuyProductOverlay}
_DYN_CURRENCIES = tuple(_BUY_PRODUCT_USING_DYN.keys())

class VehiclePreviewBottomPanelStyleBuying(VehiclePreviewBottomPanelStyleBuyingMeta):

    def __init__(self):
        super(VehiclePreviewBottomPanelStyleBuying, self).__init__()
        self.__view = None
        return

    def setStyleInfo(self, style, price, level):
        self.__view.setStyleInfo(style, price, level)

    def setBuyParams(self, buyParams):
        self.__view.setBuyParams(buyParams)

    def _makeInjectView(self):
        self.__view = _StyleBuyingPanelView()
        return self.__view


class _StyleBuyingPanelView(ViewImpl):
    __slots__ = ('__style', '__ordPrice', '__dynPrice', '__level')
    __battlePass = dependency.descriptor(IBattlePassController)
    __customizationService = dependency.descriptor(ICustomizationService)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.vehicle_preview.buying_panel.StyleBuyingPanel())
        settings.flags = ViewFlags.COMPONENT
        settings.model = StyleBuyingPanelModel()
        self.__style = None
        self.__ordPrice = {}
        self.__dynPrice = {}
        self.__level = 0
        self.__buyParams = None
        super(_StyleBuyingPanelView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(_StyleBuyingPanelView, self).getViewModel()

    def setStyleInfo(self, style, price, level):
        self.__style = style
        self.__ordPrice, self.__dynPrice = _separatePrice(price)
        self.__level = level

    def setBuyParams(self, buyParams):
        self.__buyParams = buyParams

    def _initialize(self, *args, **kwargs):
        g_currentPreviewVehicle.onChangeStarted += self.__onVehicleChangeStarted
        g_currentPreviewVehicle.onChanged += self.__onVehicleChanged
        g_clientUpdateManager.addMoneyCallback(self.__updateVMData)
        self.viewModel.onBuy += self.__onBuy

    def _finalize(self):
        self.viewModel.onBuy -= self.__onBuy
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentPreviewVehicle.onChangeStarted -= self.__onVehicleChangeStarted
        g_currentPreviewVehicle.onChanged -= self.__onVehicleChanged

    def _onLoaded(self, *args, **kwargs):
        self.__updateVMData()
        self.__applyStyle()

    def __onVehicleChangeStarted(self):
        entity = self.__hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.unsubscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)

    def __onVehicleChanged(self):
        entity = self.__hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.subscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)

    def __onVehicleLoadStarted(self):
        pass

    def __onVehicleLoadFinished(self):
        if self.__level is not None:
            self.__applyStyle()
        return

    def __updateVMData(self, *_):
        currency, price, userCurrency, level, status = self.__prepareVMData()
        with self.getViewModel().transaction() as tx:
            tx.setCurrency(currency)
            tx.setPrice(price)
            tx.setUserCurrency(userCurrency)
            tx.setLevel(level)
            tx.setStatus(status)

    def __prepareVMData(self):
        if self.__dynPrice:
            currency, price = first(((c, v) for c, v in self.__dynPrice.iteritems()))
            userCurrency = _getUserDynCurrency(currency)
            mayObtain = _mayObtainForDynCurrency(currency, price)
        else:
            money = Money(**self.__ordPrice)
            currency = money.getCurrency()
            price = money.get(currency, 0)
            userCurrency = _getUserMoney(currency)
            mayObtain = currency == Currency.GOLD or mayObtainForMoney(money) or mayObtainWithMoneyExchange(money)
        status = StyleBuyingStatus.BPNOTPASSED if not self.__battlePass.isCompleted() else (StyleBuyingStatus.AVAILABLE if mayObtain else StyleBuyingStatus.NOTENOUGHMONEY)
        return (currency,
         int(price),
         userCurrency,
         self.__level or 0,
         status)

    def __applyStyle(self):
        if self.__level:
            res = self.__customizationService.changeStyleProgressionLevelPreview(self.__level)
            if res != self.__level:
                self.__onVehicleChanged()

    def __onBuy(self, *_):
        if self.__dynPrice:
            self.__onBuyForDynamicCurrency(self.__style.userName)
        else:
            self.__onBuyForOrdinaryCurrency(self.__style.userName)

    @process
    def __onBuyForOrdinaryCurrency(self, productName):
        money = Money(**self.__ordPrice)
        if not mayObtainForMoney(money) and mayObtainWithMoneyExchange(money):
            isOk, _ = yield DialogsInterface.showDialog(ExchangeCreditsWebProductMeta(productName, 1, money.credits))
            if isOk:
                self.__onBuyForOrdinaryCurrency(productName)
                return
            return
        priceStr = formatPrice(money, reverse=True, useIcon=True)
        requestConfirmed = yield _buyRequestConfirmation(productName, priceStr)
        if requestConfirmed:
            if mayObtainForMoney(money):
                showBuyProductOverlay(self.__buyParams)
            elif money.gold > self.__itemsCache.items.stats.gold:
                showBuyGoldForBundle(money.gold, self.__buyParams)

    @process
    def __onBuyForDynamicCurrency(self, productName):
        currency, priceVal = first(((c, v) for c, v in self.__dynPrice.iteritems()))
        priceStr = formatPrice({currency: priceVal}, currency=currency, reverse=True, useIcon=True)
        requestConfirmed = yield _buyRequestConfirmation(productName, priceStr)
        if requestConfirmed:
            if _mayObtainForDynCurrency(currency, priceVal) and currency in _BUY_PRODUCT_USING_DYN:
                _BUY_PRODUCT_USING_DYN[currency](self.__buyParams)


def _separatePrice(price):
    return ({c:v for c, v in price.iteritems() if c in Currency.ALL}, {c:v for c, v in price.iteritems() if c in _DYN_CURRENCIES})


def _mayObtainForDynCurrency(currency, value):
    return value <= _getUserDynCurrency(currency)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getUserDynCurrency(currency, itemsCache=None):
    return itemsCache.items.stats.dynamicCurrencies.get(currency, 0)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getUserMoney(currency, itemsCache=None):
    return int(itemsCache.items.stats.money.get(currency))


def _buyRequestConfirmation(productName, priceStr, key='buyConfirmation'):
    return DialogsInterface.showDialog(meta=I18nConfirmDialogMeta(key=key, messageCtx={'product': productName,
     'price': priceStr}, focusedID=DIALOG_BUTTON_ID.SUBMIT))
