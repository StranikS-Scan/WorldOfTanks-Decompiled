# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/contents/exchange_content.py
import logging
from enum import Enum
from adisp import adisp_process, adisp_async
from exchange.personal_discounts_helper import getDiscountsRequiredForExchange
from gui import SystemMessages
from gui.game_control.exchange_rates_with_discounts import getCurrentTime
from gui.impl.auxiliary.exchanger import Exchanger
from gui.impl.gen import R
from gui.impl.gen.view_models.common.exchange_panel_model import ExchangePanelModel
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel
from gui.impl.gen.view_models.views.lobby.exchange.currency_model import CurrencyType
from gui.impl.lobby.exchange.currency_tab_view import getCurrencyValueFromType
from gui.impl.lobby.exchange.discount_info_tooltip import DiscountInfoTooltip, LimitedDiscountInfoTooltip
from gui.impl.lobby.exchange.discount_info_view import ExchangeDiscountView
from gui.impl.lobby.exchange.exchange_rates_helper import getRateNameFromCurrencies, handleUserValuesInput, showAllPersonalDiscountsWindow, handleAndRoundStepperInput
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class ExchangeContentResult(Enum):
    IS_OK = 0
    SERVER_ERROR = 1
    INVALID_VALUE = 2


class ExchangeContent(ExchangeDiscountView):

    def __init__(self, fromItem, toItem, viewModel=None, needItem=0):
        super(ExchangeContent, self).__init__(getRateNameFromCurrencies((fromItem.getType(), toItem.getType())), viewModel or ExchangePanelModel())
        self.__fromItem = fromItem
        self.__toItem = toItem
        self.__needItem = needItem
        self.__exchanger = Exchanger(fromItem.getType(), toItem.getType())

    def onLoading(self, *args, **kwargs):
        super(ExchangeContent, self).onLoading(*args, **kwargs)
        fromItemCount = toItemCount = 0
        if self.__needItem > 0:
            fromItemCount, toItemCount = self.__exchanger.calculateFromItemCount(self.__needItem)
        self.__fillItemsModel(fromItemCount, toItemCount)
        self._updateDiscountInfo()

    def update(self, needItem=0):
        super(ExchangeContent, self).update()
        self.__needItem = needItem
        fromItemCount = toItemCount = 0
        if self.__needItem > 0:
            fromItemCount, toItemCount = self.__exchanger.calculateFromItemCount(self.__needItem)
        self.__fillItemsModel(fromItemCount, toItemCount)

    @adisp_async
    @adisp_process
    def exchange(self, callback=None):
        if not self.__validateCount():
            callback(ExchangeContentResult.INVALID_VALUE)
        else:
            fromItemCount = self._viewModel.fromItem.getValue()
            result = yield self.__exchanger.tryExchange(fromItemCount, withConfirm=False)
            if result and result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            callback(ExchangeContentResult.SERVER_ERROR if not result.success else ExchangeContentResult.IS_OK)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.personal_exchange_rates.tooltips.ExchangeLimitTooltip():
            selectedExchangeAmount = self._viewModel.fromItem.getValue()
            return LimitedDiscountInfoTooltip(self._exchangeRate.getExchangeRateName, selectedExchangeAmount)
        return DiscountInfoTooltip(self._exchangeRate.getExchangeRateName) if contentID == R.views.lobby.personal_exchange_rates.tooltips.ExchangeRateTooltip() else super(ExchangeContent, self).createToolTipContent(event, contentID)

    def _addListeners(self):
        self._viewModel.exchangeRate.onOpenAllDiscountsWindow += self.__onOpenAllDiscountsWindow
        self._viewModel.exchangeRate.onSelectedValueUpdated += self.__onSelectedAmountChanged
        super(ExchangeContent, self)._addListeners()

    def _removeListeners(self):
        self._viewModel.exchangeRate.onOpenAllDiscountsWindow -= self.__onOpenAllDiscountsWindow
        self._viewModel.exchangeRate.onSelectedValueUpdated -= self.__onSelectedAmountChanged
        super(ExchangeContent, self)._removeListeners()

    @replaceNoneKwargsModel
    def _updateDiscountInfo(self, model=None):
        allGold = getCurrencyValueFromType(CurrencyType.GOLD)
        maxGold, maxResource = handleUserValuesInput(selectedGold=allGold, selectedCurrency=0, exchangeProvider=self._exchangeRate)
        model.exchangeRate.setMaxResourceAmountForExchange(maxResource)
        model.exchangeRate.setMaxGoldAmountForExchange(maxGold)
        self.__fillRateModel(model)
        self.__onSelectedAmountChanged({'gold': self._viewModel.fromItem.getValue()})
        super(ExchangeContent, self)._updateDiscountInfo(model=model.exchangeRate.discount)

    def __onOpenAllDiscountsWindow(self):
        showAllPersonalDiscountsWindow(exchangeRateType=self._exchangeRate.getExchangeRateName, selectedValue={'currency': self._viewModel.toItem.getValue()})

    def __onSelectedAmountChanged(self, event):
        selectedGold, selectedCurrency = handleAndRoundStepperInput(event, exchangeRate=self._exchangeRate, validateGold=True)
        self.__fillItemsModel(selectedGold, selectedCurrency)

    def __updateTooltipInformation(self):
        g_eventBus.handleEvent(events.ExchangeRatesDiscountsEvent(events.ExchangeRatesDiscountsEvent.ON_SELECTED_AMOUNT_CHANGED, {'amount': self._viewModel.fromItem.getValue()}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __validateCount(self):
        fromItemCount = self._viewModel.fromItem.getValue()
        if not self.__fromItem.isEnough(fromItemCount):
            fromItemCount = self.__fromItem.getMaxCount()
        toItemCount = self._viewModel.toItem.getValue()
        validToItemCount = self.__exchanger.calculateToItemCount(fromItemCount)
        valid = validToItemCount == toItemCount and self.__fromItem.isAvailable() and self.__toItem.isAvailable()
        if validToItemCount != toItemCount:
            self.__fillItemsModel(fromItemCount, validToItemCount)
        return valid

    def __fillItemsModel(self, fromItemCount, toItemCount):
        with self._viewModel.transaction() as ts:
            self.__fromItem.updateItemModel(ts.fromItem, fromItemCount)
            self.__toItem.updateItemModel(ts.toItem, toItemCount)
            ts.exchangeRate.setAmountOfPersonalDiscounts(len(getDiscountsRequiredForExchange(self._exchangeRate.allPersonalLimitedDiscounts, fromItemCount, getCurrentTime())))
        self.__updateTooltipInformation()

    def __fillRateModel(self, model):
        model.exchangeRate.setDefault(self.__exchanger.getDefaultRate())


class ExchangeMoneyInfo(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __walletController = dependency.descriptor(IWalletController)

    def __init__(self, currencyType=''):
        if currencyType not in Currency.ALL:
            _logger.error('%s is not Currency!', currencyType)
        self._type = currencyType

    def isEnough(self, count):
        return count <= self.__itemsCache.items.stats.money.get(self._type, 0)

    def getType(self):
        return self._type

    def isAvailable(self):
        return self.__walletController.isAvailable

    def getMaxCount(self):
        return self.__itemsCache.items.stats.money.get(self._type, 0)

    def updateItemModel(self, viewModel, count):
        viewModel.setName(self._type)
        viewModel.setValue(count)
        viewModel.setIsEnough(self.isEnough(count))
