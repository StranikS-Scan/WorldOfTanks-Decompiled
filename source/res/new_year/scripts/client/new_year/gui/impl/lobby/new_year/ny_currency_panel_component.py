# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/ny_currency_panel_component.py
import logging
from functools import partial
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyGoldUrl
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.shared.event_dispatcher import showShop
from helpers import dependency
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.ny_currency_panel_item_model import NyCurrencyPanelItemModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.ny_currency_panel_model import NyCurrencyPanelModel
from new_year.gui.impl.lobby.new_year.sub_model_presenter import SubModelPresenter
from new_year.gui.impl.lobby.new_year.tooltips.ny_currency_tooltip import NyCurrencyTooltip
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.gui.shared.ny_currency_provider import NyCurrencyProvider
from new_year.ny_constants import ViewAliases
from skeletons.gui.game_control import IWalletController
_logger = logging.getLogger(__name__)

class NyCurrencyPanelComponent(SubModelPresenter):
    __slots__ = ('__currencyProvider',)
    __CURRENCIES = (NyCurrencyType.MANDARIN, NyCurrencyType.NYGIFTMACHINETOKEN, NyCurrencyType.GOLD)
    __CURRENCY_CLICK_HANDLERS = {NyCurrencyType.NYGIFTMACHINETOKEN: partial(NewYearNavigation.switchToView, ViewAliases.SURPRISE_MACHINE_VIEW),
     NyCurrencyType.GOLD: partial(showShop, getBuyGoldUrl())}
    __wallet = dependency.descriptor(IWalletController)

    def __init__(self, viewModel, parentView, soundConfig=None):
        super(NyCurrencyPanelComponent, self).__init__(viewModel, parentView, soundConfig)
        self.__currencyProvider = NyCurrencyProvider()

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, ctID):
        if ctID == R.views.new_year.lobby.new_year.tooltips.NyCurrencyTooltip():
            currency = NyCurrencyType(event.getArgument('currency'))
            isCurrencyAvailable = event.getArgument('isCurrencyAvailable')
            return NyCurrencyTooltip(NyCurrencyType(currency), isCurrencyAvailable, allowClick=currency in self.__CURRENCY_CLICK_HANDLERS)
        return super(NyCurrencyPanelComponent, self).createToolTipContent(event, ctID)

    def initialize(self, *args, **kwargs):
        super(NyCurrencyPanelComponent, self).initialize(*args, **kwargs)
        self.__currencyProvider.initialize()
        self.__fillCurrencyList()

    def __fillCurrencyList(self):
        with self.viewModel.transaction() as model:
            items = model.getItems()
            items.clear()
            for currency in self.__CURRENCIES:
                itemModel = model.getItemsType()()
                itemModel.currency.setValue(currency)
                itemModel.setAmount(self.__currencyProvider.getCurrencyCount(currency))
                itemModel.setAllowClick(currency in self.__CURRENCY_CLICK_HANDLERS)
                itemModel.setIsCurrencyAvailable(self.__wallet.isAvailable)
                items.addViewModel(itemModel)

            items.invalidate()

    def finalize(self, *args, **kwargs):
        self.__currencyProvider.finalize()
        super(NyCurrencyPanelComponent, self).finalize()

    def _getEvents(self):
        return ((self.viewModel.onItemClick, self.__onCurrencyItemClick), (self.__currencyProvider.onCurrencyUpdated, self.__onCurrencyUpdated))

    @args2params(NyCurrencyType)
    def __onCurrencyItemClick(self, currency):
        if currency not in self.__CURRENCY_CLICK_HANDLERS:
            _logger.error('Unknown currency: %s', currency)
            return
        _logger.debug('Handle click currency: %s', currency)
        self.__CURRENCY_CLICK_HANDLERS[currency]()

    def __onCurrencyUpdated(self, *_):
        self.__fillCurrencyList()
