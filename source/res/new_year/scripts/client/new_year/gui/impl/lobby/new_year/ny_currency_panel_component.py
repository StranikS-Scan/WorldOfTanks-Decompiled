# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/ny_currency_panel_component.py
import logging
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.ny_currency_panel_item_model import NyCurrencyPanelItemModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.ny_currency_panel_model import NyCurrencyPanelModel
from new_year.gui.impl.lobby.new_year.tooltips.ny_currency_tooltip import NyCurrencyTooltip
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from new_year.gui.impl.lobby.new_year.sub_model_presenter import SubModelPresenter
from new_year.skeletons.new_year import INewYearCurrencyController
from skeletons.gui.game_control import IWalletController
from gui.impl.gui_decorators import args2params
from helpers import dependency
from gui.impl.gen import R
_logger = logging.getLogger(__name__)

class NyCurrencyPanelComponent(SubModelPresenter):
    __slots__ = ()
    __wallet = dependency.descriptor(IWalletController)
    __nyCurrencyController = dependency.descriptor(INewYearCurrencyController)

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, ctID):
        if ctID == R.views.new_year.lobby.new_year.tooltips.NyCurrencyTooltip():
            currency = NyCurrencyType(event.getArgument('currency'))
            isCurrencyAvailable = event.getArgument('isCurrencyAvailable')
            allowClick = event.getArgument('allowClick')
            if allowClick is None:
                allowClick = self.__nyCurrencyController.getCurrencyClickHandler(currency) is not None
            return NyCurrencyTooltip(currency, isCurrencyAvailable, allowClick)
        else:
            return super(NyCurrencyPanelComponent, self).createToolTipContent(event, ctID)

    def initialize(self, *args, **kwargs):
        super(NyCurrencyPanelComponent, self).initialize(*args, **kwargs)
        self.__fillCurrencyList()

    def finalize(self, *args, **kwargs):
        super(NyCurrencyPanelComponent, self).finalize()

    def _getEvents(self):
        return ((self.viewModel.onItemClick, self.__onCurrencyItemClick), (self.__nyCurrencyController.onCurrencyUpdated, self.__onCurrencyUpdated), (self.__nyCurrencyController.onVisibleCurrenciesChanged, self.__onCurrencyUpdated))

    def __fillCurrencyList(self):
        with self.viewModel.transaction() as model:
            items = model.getItems()
            items.clear()
            for currency in self.__nyCurrencyController.getCurrencies:
                itemModel = model.getItemsType()()
                itemModel.currency.setValue(currency)
                itemModel.setAmount(self.__nyCurrencyController.getCurrencyCount(currency))
                itemModel.setAllowClick(self.__nyCurrencyController.getCurrencyClickHandler(currency) is not None)
                itemModel.setIsCurrencyAvailable(self.__wallet.isAvailable)
                items.addViewModel(itemModel)

            items.invalidate()
        return

    @args2params(NyCurrencyType)
    def __onCurrencyItemClick(self, currency):
        clickHandler = self.__nyCurrencyController.getCurrencyClickHandler(currency)
        if clickHandler is None:
            _logger.error('Unknown currency: %s', currency)
            return
        else:
            _logger.debug('Handle click currency: %s', currency)
            clickHandler()
            return

    def __onCurrencyUpdated(self, *_):
        self.__fillCurrencyList()
