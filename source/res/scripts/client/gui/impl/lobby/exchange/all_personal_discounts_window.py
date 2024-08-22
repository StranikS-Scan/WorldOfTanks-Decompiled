# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/exchange/all_personal_discounts_window.py
import logging
import typing
from frameworks.wulf import WindowFlags, WindowLayer, ViewSettings
from gui.impl.gen.view_models.views.lobby.exchange.exchange_rate_all_personal_discounts_model import ExchangeRateAllPersonalDiscountsModel, CurrencyType
from gui.impl.lobby.exchange.exchange_rates_helper import EXCHANGE_RATE_NAME_TO_CURRENCIES, fillAllDiscountsModel, MAX_SHOW_DISCOUNTS_INDEX, getAllLimitedDiscountsAmount
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from skeletons.gui.game_control import IExchangeRatesWithDiscountsProvider
if typing.TYPE_CHECKING:
    from typing import Optional
    from skeletons.gui.game_control import IExchangeRateWithDiscounts
_logger = logging.getLogger(__name__)

class AllPersonalDiscountsView(ViewImpl):
    __exchangeRatesProvider = dependency.descriptor(IExchangeRatesWithDiscountsProvider)

    def __init__(self, layoutID, exchangeRateType, selectedValue=None):
        settings = ViewSettings(layoutID=layoutID, model=ExchangeRateAllPersonalDiscountsModel())
        self.__selectedValue = selectedValue or {}
        self.__exchangeRateType = exchangeRateType
        super(AllPersonalDiscountsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AllPersonalDiscountsView, self).getViewModel()

    @property
    def exchangeRate(self):
        return self.__exchangeRatesProvider.get(self.__exchangeRateType)

    def _onLoading(self, *args, **kwargs):
        super(AllPersonalDiscountsView, self)._onLoading(args, kwargs)
        self.__createModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.exchangeRate.onUpdated, self.__updateAllModel))

    def _updateModel(self, model=None):
        if self.exchangeRate is None or len(self.exchangeRate.allPersonalLimitedDiscounts) <= MAX_SHOW_DISCOUNTS_INDEX:
            _logger.debug('There are no exchangeRate or amount %s of discounts is incorrect', len(self.exchangeRate.allPersonalLimitedDiscounts))
        model.defaultExchangeRate.setGoldRateValue(self.exchangeRate.defaultRate.goldRateValue)
        model.defaultExchangeRate.setResourceRateValue(self.exchangeRate.defaultRate.resourceRateValue)
        currencyFrom, currencyTo = EXCHANGE_RATE_NAME_TO_CURRENCIES.get(self.exchangeRate.discountInfo.exchangeType)
        model.setCurrencyTypeFrom(CurrencyType(currencyFrom))
        model.setCurrencyTypeTo(CurrencyType(currencyTo))
        self.__updateDiscounts(model=model)
        return

    def __updateAllModel(self):
        if len(self.exchangeRate.allPersonalLimitedDiscounts) < 1:
            _logger.debug('There are not enough discounts for this window')
            return self.__onClose()
        self.__createModel()

    def __createModel(self):
        with self.viewModel.transaction() as model:
            self._updateModel(model=model)

    def __updateDiscounts(self, model):
        allDiscountsModel = model.getDiscounts()
        allDiscountsModel.clear()
        discounts = self.exchangeRate.allPersonalLimitedDiscounts
        if not discounts:
            _logger.debug('There are no limited discounts in the exchange')
        allDiscountsModel = fillAllDiscountsModel(allDiscountsModel=allDiscountsModel, allLimitedDiscounts=discounts, selectedPrice=self.__getSelectedGold())
        allDiscountsModel.invalidate()
        model.setAllDiscountsLimitsAmount(getAllLimitedDiscountsAmount(discounts))
        amountOfUsedDiscounts = len(allDiscountsModel)
        discountAfterLimitedLast = self.exchangeRate.unlimitedDiscountRate
        if amountOfUsedDiscounts < len(discounts):
            discountAfterLimitedLast = discounts[amountOfUsedDiscounts]
        model.commonExchangeRate.setGoldRateValue(discountAfterLimitedLast.goldRateValue)
        model.commonExchangeRate.setResourceRateValue(discountAfterLimitedLast.resourceRateValue)

    def __getSelectedGold(self):
        selectedGold = self.__selectedValue.get('gold', 0)
        selectedCurrency = self.__selectedValue.get('currency', 0)
        if selectedCurrency > 0:
            selectedGold, _ = self.exchangeRate.calculateResourceToExchange(selectedCurrency)
        return selectedGold

    def __onClose(self):
        self.destroy()


class AllPersonalDiscountsWindow(LobbyWindow):

    def __init__(self, layoutID, exchangeRateType, selectedValue):
        super(AllPersonalDiscountsWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=AllPersonalDiscountsView(layoutID=layoutID, exchangeRateType=exchangeRateType, selectedValue=selectedValue), layer=WindowLayer.OVERLAY)
