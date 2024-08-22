# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/exchange/base_exchange_window.py
import typing
from exchange.personal_discounts_helper import getDiscountsRequiredForExchange
from gui import SystemMessages
from gui.game_control.exchange_rates_with_discounts import getCurrentTime
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.exchange.currency_model import CurrencyType
from gui.impl.gen.view_models.views.lobby.exchange.exchange_rate_base_model import ExchangeRateBaseModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.common.components_presenter import ComponentsPresenterView
from gui.impl.lobby.exchange.currency_tab_view import CurrenciesTabView, getCurrencyValueFromType
from gui.impl.lobby.exchange.discount_info_tooltip import DiscountInfoTooltip, LimitedDiscountInfoTooltip
from gui.impl.lobby.exchange.discount_info_view import ExchangeDiscountView
from gui.impl.lobby.exchange.exchange_rates_helper import setDiscountViewed, isDiscountViewed, handleUserValuesInput, showAllPersonalDiscountsWindow, handleAndRoundStepperInput
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.game_control import IWalletController, IExchangeRatesWithDiscountsProvider
if typing.TYPE_CHECKING:
    from typing import Optional
    from skeletons.gui.game_control import IExchangeRateWithDiscounts

class BaseExchangeWindow(ComponentsPresenterView, FullScreenDialogBaseView):
    _wallet = dependency.descriptor(IWalletController)
    __exchangeRatesProvider = dependency.descriptor(IExchangeRatesWithDiscountsProvider)
    __BLUR_INTENSITY = 0.8

    def __init__(self, settings, exchangeRateType, ctx=None):
        ctx = ctx or {}
        self._initValues = ctx
        self.__backgroundImage = ctx.pop('backgroundImage', 0)
        self.__exchangeRateType = exchangeRateType
        self.__blur = ctx.pop('blur', None)
        super(BaseExchangeWindow, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(BaseExchangeWindow, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.personal_exchange_rates.tooltips.ExchangeLimitTooltip():
            selectedExchangeAmount = self.viewModel.getGoldAmountForExchange()
            return LimitedDiscountInfoTooltip(self.exchangeRate.getExchangeRateName, selectedExchangeAmount)
        return DiscountInfoTooltip(self.exchangeRate.getExchangeRateName) if contentID == R.views.lobby.personal_exchange_rates.tooltips.ExchangeRateTooltip() else super(BaseExchangeWindow, self).createToolTipContent(event, contentID)

    @property
    def exchangeRate(self):
        return self.__exchangeRatesProvider.get(self.__exchangeRateType)

    def _onLoading(self, *args, **kwargs):
        super(BaseExchangeWindow, self)._onLoading(args, kwargs)
        if self.__blur is not None:
            self.__blur = CachedBlur(enabled=True, ownLayer=self.getWindow().layer - 1, blurRadius=self.__BLUR_INTENSITY)
        self.viewModel.setBackground(self.__backgroundImage)
        self._updateAllModel()
        if not isDiscountViewed(self.__exchangeRateType):
            setDiscountViewed(self.__exchangeRateType, forced=True)
            g_eventBus.handleEvent(events.ExchangeRatesDiscountsEvent(events.ExchangeRatesDiscountsEvent.ON_PERSONAL_DISCOUNT_VIEWED, {'type': self.__exchangeRateType}), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def _finalize(self):
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        super(BaseExchangeWindow, self)._finalize()
        return

    def _getEvents(self):
        eventsTuple = super(BaseExchangeWindow, self)._getEvents()
        return eventsTuple + ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onExchange, self._onExchange),
         (self.viewModel.onSelectedValueUpdated, self.__onSelectedAmountChanged),
         (self.viewModel.onOpenAllDiscountsWindow, self._onOpenAllDiscountsWindow),
         (self.exchangeRate.onUpdated, self._updateAllModel))

    def _getCallbacks(self):
        return (('stats.gold', self.__updateData),)

    def _updateAllModel(self):
        if self.exchangeRate is None:
            return
        else:
            with self.viewModel.transaction() as model:
                self._updateModel(model=model)
            return

    def _updateModel(self, model=None):
        self.__setExchangeDiscountsInfo(model=model)
        self._onSelectedValueChanged(model=model)

    def _registerSubModels(self):
        return [CurrenciesTabView(self.viewModel.balance, self), ExchangeDiscountView(self.exchangeRate.getExchangeRateName, self.viewModel.discount)]

    @replaceNoneKwargsModel
    def _onSelectedValueChanged(self, params=None, model=None):
        if not params:
            currentValue = model.getResourceAmountForExchange()
            params = self._initValues if not currentValue else {'currency': currentValue}
        selectedGold, selectedCurrency = handleAndRoundStepperInput(params, exchangeRate=self.exchangeRate, validateGold=True)
        self._setStepperValues(selectedGold, selectedCurrency, model=model)

    @replaceNoneKwargsModel
    def _setStepperValues(self, selectedGold, selectedCurrency, model=None):
        model.setGoldAmountForExchange(selectedGold)
        model.setResourceAmountForExchange(selectedCurrency)
        model.setAmountOfPersonalDiscounts(self._getDiscountsRequiredForExchange(goldForExchange=selectedGold))

    def _onOpenAllDiscountsWindow(self):
        showAllPersonalDiscountsWindow(exchangeRateType=self.__exchangeRateType, selectedValue={'currency': self.viewModel.getResourceAmountForExchange()})

    def _processResult(self, result, exchangeAmount):
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self.destroy()

    def _onExchange(self, event):
        raise NotImplementedError

    def _setMaxAmountForExchange(self, maxGold, maxResource, model):
        maxGold, maxResource = handleUserValuesInput(selectedGold=maxGold, selectedCurrency=0, exchangeProvider=self.exchangeRate)
        model.setAmountOfPersonalDiscounts(self._getDiscountsRequiredForExchange(goldForExchange=maxGold))
        model.setMaxResourceAmountForExchange(maxResource)
        model.setMaxGoldAmountForExchange(maxGold)

    def _getDiscountsRequiredForExchange(self, goldForExchange):
        return len(getDiscountsRequiredForExchange(self.exchangeRate.allPersonalLimitedDiscounts, goldForExchange, getCurrentTime()))

    def __setExchangeDiscountsInfo(self, model):
        model.exchangeRate.setGoldRateValue(self.exchangeRate.unlimitedRateAfterMainDiscount.goldRateValue)
        model.exchangeRate.setResourceRateValue(self.exchangeRate.unlimitedRateAfterMainDiscount.resourceRateValue)
        allGold = getCurrencyValueFromType(CurrencyType.GOLD)
        self._setMaxAmountForExchange(maxGold=allGold, maxResource=0, model=model)

    def __onSelectedAmountChanged(self, params):
        with self.viewModel.transaction() as model:
            self._onSelectedValueChanged(params, model=model)
        g_eventBus.handleEvent(events.ExchangeRatesDiscountsEvent(events.ExchangeRatesDiscountsEvent.ON_SELECTED_AMOUNT_CHANGED, {'amount': self.viewModel.getGoldAmountForExchange()}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __updateData(self, *args):
        self._updateAllModel()

    def __onClose(self):
        self.destroyWindow()
