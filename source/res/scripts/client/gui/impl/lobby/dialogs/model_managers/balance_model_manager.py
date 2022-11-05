# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/model_managers/balance_model_manager.py
import logging
import constants
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.gen.view_models.views.common_balance_content_model import CommonBalanceContentModel
from shared_utils import CONST_CONTAINER
from frameworks.wulf import NumberFormatType
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen.view_models.ui_kit.currency_item_model import CurrencyItemModel
from gui.impl.gen.view_models.views.value_price import ValuePrice
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IWalletController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class CurrencyStatus(CONST_CONTAINER):
    IN_PROGRESS = 0
    NOT_AVAILABLE = 1
    AVAILABLE = 2


class BalanceModelManager(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)
    __gui = dependency.descriptor(IGuiLoader)
    __slots__ = ('__stats', '__currencyIndexes', '__isGoldAutoPurchaseEnabled', '__viewModel')
    __CURRENCY_FORMATTER = {Currency.CREDITS: NumberFormatType.INTEGRAL,
     Currency.GOLD: NumberFormatType.GOLD,
     Currency.CRYSTAL: NumberFormatType.INTEGRAL,
     'freeXP': NumberFormatType.INTEGRAL}
    __SPECIAL_TOOLTIPS = {Currency.GOLD: TOOLTIPS_CONSTANTS.GOLD_STATS,
     Currency.CREDITS: TOOLTIPS_CONSTANTS.CREDITS_STATS}

    def __init__(self, viewModel, *args, **kwargs):
        super(BalanceModelManager, self).__init__(*args, **kwargs)
        self.__currencyIndexes = []
        self.__viewModel = viewModel
        self.__stats = None
        self.__isGoldAutoPurchaseEnabled = False
        return

    @property
    def viewModel(self):
        return self.__viewModel

    def start(self, currencies):
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyUpdated)
        g_clientUpdateManager.addCallback('stats.freeXP', self.__onFreeXpUpdated)
        self.__wallet.onWalletStatusChanged += self.__onWalletChanged
        self.__stats = self.__itemsCache.items.stats
        self.__isGoldAutoPurchaseEnabled = self.__wallet.isAvailable
        for currency in currencies:
            if currency == ValuePrice.FREE_XP:
                self.__addCurrency(ValuePrice.FREE_XP, self.__getCurrencyFormat(ValuePrice.FREE_XP, self.__stats.actualFreeXP))
                self.__onCurrencyUpdated(currency, self.__stats.actualFreeXP)
            self.__addCurrency(currency, self.__getCurrencyFormat(currency, self.__stats.actualMoney.get(currency)))
            self.__onCurrencyUpdated(currency, self.__stats.actualMoney.get(currency))

    def stop(self):
        self.__wallet.onWalletStatusChanged -= self.__onWalletChanged
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __addCurrency(self, currency, value):
        currencyModel = CurrencyItemModel()
        currencyModel.setCurrency(currency)
        currencyModel.setValue(value)
        if constants.IS_SINGAPORE and currency in self.__SPECIAL_TOOLTIPS:
            currencyModel.setSpecialTooltip(self.__SPECIAL_TOOLTIPS[currency])
        else:
            currencyModel.setSpecialTooltip('')
        self.viewModel.currency.addViewModel(currencyModel)
        self.__currencyIndexes.append(currency)

    def __getCurrencyFormat(self, currency, value):
        if currency in self.__CURRENCY_FORMATTER:
            formatType = self.__CURRENCY_FORMATTER[currency]
        else:
            formatType = NumberFormatType.INTEGRAL
        return self.__gui.systemLocale.getNumberFormat(value, formatType=formatType)

    def __onFreeXpUpdated(self, value):
        self.__onCurrencyUpdated('freeXP', value)

    def __onMoneyUpdated(self, _):
        for currency in Currency.GUI_ALL:
            moneyValue = self.__stats.actualMoney.get(currency)
            self.__onCurrencyUpdated(currency, moneyValue)

    def __onCurrencyUpdated(self, currency, value):
        if currency in self.__currencyIndexes:
            index = self.__currencyIndexes.index(currency)
            self.viewModel.currency.getItem(index).setValue(self.__getCurrencyFormat(currency, value) if value is not None and self.__isGoldAutoPurchaseEnabled else '')
        return

    def __onWalletChanged(self, status):
        self.__isGoldAutoPurchaseEnabled &= self.__wallet.isAvailable
        for currency in Currency.GUI_ALL:
            self.__onCurrencyUpdated(currency, self.__stats.actualMoney.get(currency) if status[currency] == CurrencyStatus.AVAILABLE else None)

        self.__onCurrencyUpdated('freeXP', self.__stats.actualFreeXP if status['freeXP'] == CurrencyStatus.AVAILABLE else None)
        return
