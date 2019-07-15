# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/contents/common_balance_content.py
import logging
from gui.impl.gen.view_models.views.common_balance_content_model import CommonBalanceContentModel
from shared_utils import CONST_CONTAINER
from frameworks.wulf import ViewFlags, NumberFormatType
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen import R
from gui.impl.gen.view_models.ui_kit.currency_item_model import CurrencyItemModel
from gui.impl.pub.view_impl import ViewImpl
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class CurrencyStatus(CONST_CONTAINER):
    IN_PROGRESS = 0
    NOT_AVAILABLE = 1
    AVAILABLE = 2


class CommonBalanceContent(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)
    __slots__ = ('__stats', '__currencyIndexes')
    __CURRENCY_FORMATTER = {Currency.CREDITS: NumberFormatType.INTEGRAL,
     Currency.GOLD: NumberFormatType.GOLD,
     Currency.CRYSTAL: NumberFormatType.INTEGRAL,
     'freeXP': NumberFormatType.INTEGRAL}

    def __init__(self, *args, **kwargs):
        super(CommonBalanceContent, self).__init__(R.views.common.dialog_view.components.balance_contents.CommonBalanceContent(), ViewFlags.COMPONENT, CommonBalanceContentModel, *args, **kwargs)
        self.__currencyIndexes = []

    @property
    def viewModel(self):
        return super(CommonBalanceContent, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(CommonBalanceContent, self)._initialize()
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyUpdated)
        g_clientUpdateManager.addCallback('stats.freeXP', self.__onFreeXpUpdated)
        self.__wallet.onWalletStatusChanged += self.__onWalletChanged
        self.__stats = self.__itemsCache.items.stats
        for currency in Currency.GUI_ALL:
            self.__addCurrency(currency, self.__getCurrencyFormat(currency, self.__stats.actualMoney.get(currency)))

        self.__addCurrency('freeXP', self.__getCurrencyFormat('freeXP', self.__stats.actualFreeXP))

    def _finalize(self):
        super(CommonBalanceContent, self)._finalize()
        self.__wallet.onWalletStatusChanged -= self.__onWalletChanged
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __addCurrency(self, currency, value):
        button = CurrencyItemModel()
        button.setCurrency(currency)
        button.setValue(value)
        self.viewModel.currency.addViewModel(button)
        self.__currencyIndexes.append(currency)

    def __getCurrencyFormat(self, currency, value):
        if currency in self.__CURRENCY_FORMATTER:
            formatType = self.__CURRENCY_FORMATTER[currency]
        else:
            formatType = NumberFormatType.INTEGRAL
        return self.gui.systemLocale.getNumberFormat(value, formatType=formatType)

    def __onFreeXpUpdated(self, value):
        self.__onCurrencyUpdated('freeXP', value)

    def __onMoneyUpdated(self, _):
        for currency in Currency.GUI_ALL:
            moneyValue = self.__stats.actualMoney.get(currency)
            self.__onCurrencyUpdated(currency, moneyValue)

    def __onCurrencyUpdated(self, currency, value):
        index = self.__currencyIndexes.index(currency)
        self.viewModel.currency.getItem(index).setValue(self.__getCurrencyFormat(currency, value) if value is not None else '')
        return

    def __onWalletChanged(self, status):
        for currency in Currency.GUI_ALL:
            self.__onCurrencyUpdated(currency, self.__stats.actualMoney.get(currency) if status[currency] == CurrencyStatus.AVAILABLE else None)

        self.__onCurrencyUpdated('freeXP', self.__stats.actualFreeXP if status['freeXP'] == CurrencyStatus.AVAILABLE else None)
        return
