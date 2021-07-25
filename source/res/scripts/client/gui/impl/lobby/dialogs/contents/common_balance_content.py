# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/contents/common_balance_content.py
import logging
from itertools import chain
import constants
from frameworks.wulf import NumberFormatType, ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.impl import backport
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.ui_kit.currency_item_model import CurrencyItemModel
from gui.impl.gen.view_models.views.common_balance_content_model import CommonBalanceContentModel
from gui.impl.gen.view_models.views.value_price import ValuePrice
from gui.impl.pub.view_impl import ViewImpl
from gui.shared.money import Currency
from helpers import dependency
from shared_utils import CONST_CONTAINER
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
    __slots__ = ('__stats', '__currencyIndexes', '__isGoldAutoPurhaseEnabled')
    __CURRENCY_FORMATTER = {Currency.CREDITS: NumberFormatType.INTEGRAL,
     Currency.GOLD: NumberFormatType.GOLD,
     Currency.CRYSTAL: NumberFormatType.INTEGRAL,
     ValuePrice.FREE_XP: NumberFormatType.INTEGRAL}
    __CURRENCY_NOT_AVAILABLE_TOOLTIPS = {Currency.CREDITS: (R.strings.tooltips.header.buttons.credits.header(), R.strings.tooltips.wallet.not_available_credits.body()),
     Currency.GOLD: (R.strings.tooltips.header.buttons.gold.header(), R.strings.tooltips.wallet.not_available_gold.body()),
     Currency.CRYSTAL: (R.strings.tooltips.header.buttons.crystal.header(), R.strings.tooltips.wallet.not_available_crystal.body()),
     ValuePrice.FREE_XP: (R.strings.tooltips.header.buttons.freeXP.header(), R.strings.tooltips.wallet.not_available_freexp.body())}

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.common.dialog_view.components.balance_contents.CommonBalanceContent())
        settings.model = CommonBalanceContentModel()
        settings.args = args
        settings.kwargs = kwargs
        super(CommonBalanceContent, self).__init__(settings, *args, **kwargs)
        self.__currencyIndexes = []

    @property
    def viewModel(self):
        return super(CommonBalanceContent, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(True,)), self.getParentWindow())
            window.load()
            return window
        else:
            return super(CommonBalanceContent, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        super(CommonBalanceContent, self)._initialize()
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyUpdated)
        g_clientUpdateManager.addCallback('stats.freeXP', self.__onFreeXpUpdated)
        self.__wallet.onWalletStatusChanged += self.__onWalletChanged
        self.__stats = self.__itemsCache.items.stats
        self.__isGoldAutoPurhaseEnabled = self.__wallet.isAvailable
        currencies = kwargs.get('currencies', chain(Currency.GUI_ALL, (ValuePrice.FREE_XP,)))
        for currency in currencies:
            if currency == ValuePrice.FREE_XP:
                self.__addCurrency(ValuePrice.FREE_XP, self.__getCurrencyFormat(ValuePrice.FREE_XP, self.__stats.actualFreeXP))
                self.__onCurrencyUpdated(currency, self.__stats.actualFreeXP)
            self.__addCurrency(currency, self.__getCurrencyFormat(currency, self.__stats.actualMoney.get(currency)))
            self.__onCurrencyUpdated(currency, self.__stats.actualMoney.get(currency))

    def _finalize(self):
        super(CommonBalanceContent, self)._finalize()
        self.__wallet.onWalletStatusChanged -= self.__onWalletChanged
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __addCurrency(self, currency, value):
        currencyModel = CurrencyItemModel()
        currencyModel.setCurrency(currency)
        currencyModel.setValue(value)
        if constants.IS_SINGAPORE and currency in CURRENCIES_CONSTANTS.SINGAPORE_ALTERNATIVE_CURRENCIES_SET:
            currencyModel.setSpecialTooltip(currency + 'StatsFullScreen')
        elif not constants.IS_SINGAPORE:
            currencyModel.setSpecialTooltip(currency + 'InfoFullScreen')
        naTooltip = self.__CURRENCY_NOT_AVAILABLE_TOOLTIPS[currency]
        currencyModel.setTooltipHeader(backport.text(naTooltip[0]))
        currencyModel.setTooltipBody(backport.text(naTooltip[1]))
        self.viewModel.currency.addViewModel(currencyModel)
        self.__currencyIndexes.append(currency)

    def __getCurrencyFormat(self, currency, value):
        if currency in self.__CURRENCY_FORMATTER:
            formatType = self.__CURRENCY_FORMATTER[currency]
        else:
            formatType = NumberFormatType.INTEGRAL
        return self.gui.systemLocale.getNumberFormat(value, formatType=formatType)

    def __onFreeXpUpdated(self, value):
        self.__onCurrencyUpdated(ValuePrice.FREE_XP, value)

    def __onMoneyUpdated(self, _):
        for currency in Currency.GUI_ALL:
            moneyValue = self.__stats.actualMoney.get(currency)
            self.__onCurrencyUpdated(currency, moneyValue)

    def __onCurrencyUpdated(self, currency, value):
        if currency in self.__currencyIndexes:
            index = self.__currencyIndexes.index(currency)
            self.viewModel.currency.getItem(index).setValue(self.__getCurrencyFormat(currency, value) if value is not None and self.__isGoldAutoPurhaseEnabled else '')
        return

    def __onWalletChanged(self, status):
        self.__isGoldAutoPurhaseEnabled &= self.__wallet.isAvailable
        for currency in Currency.GUI_ALL:
            self.__onCurrencyUpdated(currency, self.__stats.actualMoney.get(currency) if status[currency] == CurrencyStatus.AVAILABLE else None)

        self.__onCurrencyUpdated(ValuePrice.FREE_XP, self.__stats.actualFreeXP if status[ValuePrice.FREE_XP] == CurrencyStatus.AVAILABLE else None)
        return
