# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/exchange/discount_info_tooltip.py
import logging
import typing
from exchange.personal_discounts_constants import ExchangeRateShowFormat, ExchangeRate
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.exchange.exchange_discount_tooltip_model import ExchangeDiscountTooltipModel, CurrencyType
from gui.impl.gen.view_models.views.lobby.exchange.limited_exchange_discount_tooltip_model import LimitedExchangeDiscountTooltipModel
from gui.impl.lobby.exchange.exchange_rates_helper import EXCHANGE_RATE_NAME_TO_CURRENCIES, MAX_SHOW_DISCOUNTS_INDEX, fillAllDiscountsModel, getAllLimitedDiscountsAmount
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.game_control import IExchangeRatesWithDiscountsProvider
if typing.TYPE_CHECKING:
    from typing import Optional
    from exchange.personal_discounts_constants import ExchangeDiscountInfo
    from skeletons.gui.game_control import IExchangeRateWithDiscounts
_logger = logging.getLogger(__name__)

class DiscountInfoTooltip(ViewImpl):
    __exchangeRateProvider = dependency.descriptor(IExchangeRatesWithDiscountsProvider)

    def __init__(self, exchangeType, contentID=None, model=None, *args):
        self.__exchangeType = exchangeType
        settings = ViewSettings(contentID or R.views.lobby.personal_exchange_rates.tooltips.ExchangeRateTooltip(), flags=ViewFlags.VIEW, model=model or ExchangeDiscountTooltipModel(), args=args)
        super(DiscountInfoTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def exchangeRate(self):
        return self.__exchangeRateProvider.get(self.__exchangeType)

    @property
    def discount(self):
        return self.exchangeRate.discountInfo

    @property
    def defaultRate(self):
        return self.exchangeRate.defaultRate

    @property
    def commonRate(self):
        return self.exchangeRate.commonServerDiscountRate

    @property
    def personalDiscountRate(self):
        return self.exchangeRate.unlimitedDiscountRate

    def _getEvents(self):
        return ((self.exchangeRate.onUpdated, self.__updateData),)

    def _onLoading(self, *args, **kwargs):
        self.__updateData()
        super(DiscountInfoTooltip, self)._onLoading()

    @replaceNoneKwargsModel
    def _update(self, model=None):
        model.defaultExchangeRate.setGoldRateValue(self.defaultRate.goldRateValue)
        model.defaultExchangeRate.setResourceRateValue(self.defaultRate.resourceRateValue)
        model.commonExchangeRate.setGoldRateValue(self.commonRate.goldRateValue)
        model.commonExchangeRate.setResourceRateValue(self.commonRate.resourceRateValue)
        model.personalExchangeRate.setGoldRateValue(self.personalDiscountRate.goldRateValue)
        model.personalExchangeRate.setResourceRateValue(self.personalDiscountRate.resourceRateValue)
        model.setIsTemporary(self.discount.showFormat == ExchangeRateShowFormat.TEMPORARY)
        currencyFrom, currencyTo = EXCHANGE_RATE_NAME_TO_CURRENCIES.get(self.discount.exchangeType)
        model.setCurrencyTypeFrom(CurrencyType(currencyFrom))
        model.setCurrencyTypeTo(CurrencyType(currencyTo))

    def __updateData(self):
        if self.exchangeRate is None or self.discount is None:
            _logger.error('ExchangeRate is None or discount is None in the tooltip')
            return
        else:
            self._update()
            return


class LimitedDiscountInfoTooltip(DiscountInfoTooltip):

    def __init__(self, exchangeType, selectedExchangeAmount, *args):
        self.__selectedGoldAmount = selectedExchangeAmount
        super(LimitedDiscountInfoTooltip, self).__init__(exchangeType, R.views.lobby.personal_exchange_rates.tooltips.ExchangeLimitTooltip(), LimitedExchangeDiscountTooltipModel(), args)

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def commonRate(self):
        allDiscountsAvailable = self.exchangeRate.allPersonalLimitedDiscounts
        amountOfUsedDiscounts = len(self.viewModel.getDiscounts())
        discountAfterLimitedLast = self.exchangeRate.unlimitedDiscountRate
        if amountOfUsedDiscounts < len(allDiscountsAvailable):
            discountAfterLimitedLast = allDiscountsAvailable[amountOfUsedDiscounts]
        return discountAfterLimitedLast

    def _getListeners(self):
        super(LimitedDiscountInfoTooltip, self)._getListeners()
        return ((events.ExchangeRatesDiscountsEvent.ON_SELECTED_AMOUNT_CHANGED, self.__updateSelectedAmount, EVENT_BUS_SCOPE.LOBBY),)

    @replaceNoneKwargsModel
    def _update(self, model=None):
        if not self.exchangeRate.allPersonalLimitedDiscounts:
            _logger.error('There are no limited discounts in the exchange')
        allDiscountsModel = model.getDiscounts()
        allDiscountsModel.clear()
        amountOfDiscountsToShow = min(len(self.exchangeRate.allPersonalLimitedDiscounts), MAX_SHOW_DISCOUNTS_INDEX)
        allDiscounts = self.exchangeRate.allPersonalLimitedDiscounts[:amountOfDiscountsToShow]
        allDiscountsModel = fillAllDiscountsModel(allDiscountsModel=allDiscountsModel, allLimitedDiscounts=allDiscounts, selectedPrice=self.__selectedGoldAmount)
        allDiscountsModel.invalidate()
        model.setAllDiscountsLimitsAmount(getAllLimitedDiscountsAmount(self.exchangeRate.allPersonalLimitedDiscounts))
        super(LimitedDiscountInfoTooltip, self)._update(model=model)

    def __updateSelectedAmount(self, event):
        self.__selectedGoldAmount = event.ctx.get('amount', 0)
        self._update()
