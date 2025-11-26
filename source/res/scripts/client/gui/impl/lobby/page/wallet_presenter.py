# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/wallet_presenter.py
from __future__ import absolute_import
import logging
import typing
from future.utils import itervalues
from helpers.events_handler import EventsHandler
from Event import Event
from adisp import adisp_process
from constants import IS_SINGAPORE
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyGoldUrl
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.game_control.wallet import WalletController
from gui.impl.gen.view_models.views.lobby.page.header.currency_model import CurrencyModel
from gui.impl.gen.view_models.views.lobby.page.header.wallet_model import WalletModel
from gui.impl.pub.view_component import ViewComponent
from gui.shared import event_dispatcher as shared_events
from gui.shared.event_dispatcher import showShop
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IWalletController, IExchangeRatesWithDiscountsProvider
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class CurrencyStatusProvider(EventsHandler):
    _itemsCache = dependency.descriptor(IItemsCache)
    _wallet = dependency.descriptor(IWalletController)

    def __init__(self, currencyType):
        super(CurrencyStatusProvider, self).__init__()
        self._currencyType = currencyType
        self.onChanged = Event()

    def initialize(self):
        self._subscribe()

    def finalize(self):
        self.onChanged.clear()
        self._unsubscribe()

    def getCurrencyType(self):
        return self._currencyType

    def createModel(self):
        return CurrencyModel()

    def fillModel(self, currencyModel):
        raise NotImplementedError

    def doAction(self):
        raise NotImplementedError

    def _changed(self, *args):
        self.onChanged(self._currencyType)

    def _getCallbacks(self):
        return (('stats.{}'.format(self._currencyType), self._changed),)


class CrystalProvider(CurrencyStatusProvider):

    def __init__(self, currencyType=Currency.CRYSTAL):
        super(CrystalProvider, self).__init__(currencyType=currencyType)

    def fillModel(self, currencyModel):
        currencyModel.setValue(self._itemsCache.items.stats.actualMoney.crystal)
        currencyModel.setTooltipType(TOOLTIPS_CONSTANTS.CRYSTAL_INFO_FULL_SCREEN)
        currencyModel.setDiscount(False)
        walletStatus = self._wallet.componentsStatuses[self.getCurrencyType()]
        currencyModel.setStatus(WalletController.STATUS.getKeyByValue(walletStatus))

    def doAction(self):
        shared_events.showCrystalWindow()

    def _getEvents(self):
        return ((self._wallet.onWalletStatusChanged, self._changed),)


class GoldProvider(CurrencyStatusProvider):
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, currencyType=Currency.GOLD):
        super(GoldProvider, self).__init__(currencyType=currencyType)

    def fillModel(self, currencyModel):
        if IS_SINGAPORE:
            tooltipConstant = TOOLTIPS_CONSTANTS.GOLD_STATS
        else:
            tooltipConstant = TOOLTIPS_CONSTANTS.GOLD_INFO_FULL_SCREEN
        currencyModel.setValue(self._itemsCache.items.stats.actualMoney.gold)
        currencyModel.setTooltipType(tooltipConstant)
        currencyModel.setDiscount(False)
        walletStatus = self._wallet.componentsStatuses[self.getCurrencyType()]
        currencyModel.setStatus(WalletController.STATUS.getKeyByValue(walletStatus))

    @adisp_process
    def doAction(self):
        navigationPossible = yield self._lobbyContext.isHeaderNavigationPossible()
        if navigationPossible:
            showShop(getBuyGoldUrl())

    def _getEvents(self):
        return ((self._wallet.onWalletStatusChanged, self._changed),)


class CreditsProvider(CurrencyStatusProvider):
    _exchangeRates = dependency.descriptor(IExchangeRatesWithDiscountsProvider)

    def __init__(self, currencyType=Currency.CREDITS):
        super(CreditsProvider, self).__init__(currencyType=currencyType)

    def fillModel(self, currencyModel):
        if IS_SINGAPORE:
            tooltipConstant = TOOLTIPS_CONSTANTS.CREDITS_STATS
        else:
            tooltipConstant = TOOLTIPS_CONSTANTS.CREDITS_INFO_FULL_SCREEN
        currencyModel.setValue(self._itemsCache.items.stats.actualMoney.credits)
        currencyModel.setTooltipType(tooltipConstant)
        currencyModel.setDiscount(self._exchangeRates.goldToCredits.isDiscountAvailable())
        walletStatus = self._wallet.componentsStatuses[self.getCurrencyType()]
        currencyModel.setStatus(WalletController.STATUS.getKeyByValue(walletStatus))

    def doAction(self):
        shared_events.showExchangeCurrencyWindow()

    def _getEvents(self):
        return ((self._wallet.onWalletStatusChanged, self._changed), (self._exchangeRates.goldToCredits.onUpdated, self._changed))


class FreeXpProvider(CurrencyStatusProvider):
    _exchangeRates = dependency.descriptor(IExchangeRatesWithDiscountsProvider)

    def __init__(self, currencyType=Currency.FREE_XP):
        super(FreeXpProvider, self).__init__(currencyType=currencyType)

    def fillModel(self, currencyModel):
        currencyModel.setValue(self._itemsCache.items.stats.actualFreeXP)
        currencyModel.setTooltipType(TOOLTIPS_CONSTANTS.FREEXP_INFO_FULL_SCREEN)
        currencyModel.setDiscount(self._exchangeRates.freeXpTranslation.isDiscountAvailable())
        walletStatus = self._wallet.componentsStatuses[self.getCurrencyType()]
        currencyModel.setStatus(WalletController.STATUS.getKeyByValue(walletStatus))

    def doAction(self):
        shared_events.showExchangeXPWindow()

    def _getEvents(self):
        return ((self._wallet.onWalletStatusChanged, self._changed), (self._exchangeRates.freeXpTranslation.onUpdated, self._changed))


class WalletPresenter(ViewComponent[WalletModel]):

    def __init__(self, currencyStatusProviders=None, model=WalletModel):
        super(WalletPresenter, self).__init__(model=model)
        self._currencyProviders = {}
        for provider in currencyStatusProviders:
            curType = provider.getCurrencyType()
            if curType in self._currencyProviders:
                _logger.error('Currency type is already added: %s', curType)
            self._currencyProviders[curType] = provider

    @property
    def viewModel(self):
        return super(WalletPresenter, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onCurrencyAction, self.__onCurrencyAction),)

    def _onLoading(self, *args, **kwargs):
        super(WalletPresenter, self)._onLoading(*args, **kwargs)
        for cp in itervalues(self._currencyProviders):
            cp.initialize()
            cp.onChanged += self.__onCurrencyChanged

        self.__onCurrenciesUpdate()

    def _finalize(self):
        for cp in itervalues(self._currencyProviders):
            cp.onChanged -= self.__onCurrencyChanged
            cp.finalize()

        self._currencyProviders = None
        super(WalletPresenter, self)._finalize()
        return

    def __onCurrencyChanged(self, currencyType):
        currencyWatcher = self._currencyProviders.get(currencyType)
        with self.viewModel.getCurrencies() as currencies:
            currency = currencies.get(currencyType)
            if currency is None:
                currency = currencyWatcher.createModel()
                currencies.set(currencyType, currency)
            currencyWatcher.fillModel(currency)
        return

    def __onCurrenciesUpdate(self):
        for currencyType in self._currencyProviders:
            self.__onCurrencyChanged(currencyType)

    def __onCurrencyAction(self, args):
        curType = args.get('type')
        currencyWatcher = self._currencyProviders.get(curType, None)
        if currencyWatcher is None:
            _logger.error('Currency type is invalid: %s', curType)
            return
        else:
            currencyWatcher.doAction()
            return
