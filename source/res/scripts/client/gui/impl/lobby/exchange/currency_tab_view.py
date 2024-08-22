# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/exchange/currency_tab_view.py
import logging
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen.view_models.views.lobby.exchange.currency_model import CurrencyType, CurrencyModel
from gui.impl.gen.view_models.views.lobby.exchange.currency_tab_model import CurrencyTabModel
from helpers import dependency
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_TYPE_TO_VALUE_PATH = {CurrencyType.CREDITS: 'actualCredits',
 CurrencyType.GOLD: 'actualGold',
 CurrencyType.CRYSTAL: 'actualCrystal',
 CurrencyType.FREEXP: 'actualFreeXP'}
_CURRENCY_TOOLTIPS = {CurrencyType.GOLD: TOOLTIPS_CONSTANTS.RESOURCE_WELL_GOLD,
 CurrencyType.CREDITS: TOOLTIPS_CONSTANTS.RESOURCE_WELL_CREDITS,
 CurrencyType.CRYSTAL: TOOLTIPS_CONSTANTS.RESOURCE_WELL_CRYSTAL,
 CurrencyType.FREEXP: TOOLTIPS_CONSTANTS.RESOURCE_WELL_FREE_XP}

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getCurrencyValueFromType(currencyType, itemsCache=None):
    currencyValuePath = _TYPE_TO_VALUE_PATH.get(currencyType, None)
    if currencyValuePath is not None:
        value = getattr(itemsCache.items.stats, currencyValuePath)
        return value
    else:
        return


class CurrenciesTabView(SubModelPresenter):
    __slots__ = ('__tooltipData',)
    __wallet = dependency.descriptor(IWalletController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        self.__tooltipData = {}
        super(CurrenciesTabView, self).__init__(*args, **kwargs)

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        super(CurrenciesTabView, self).initialize(*args, **kwargs)
        self.__updateCurrencies()

    def finalize(self):
        self.__tooltipData = {}
        super(CurrenciesTabView, self).finalize()

    def _getCallbacks(self):
        return (('stats.gold', self.__onBalanceUpdated),
         ('stats.credits', self.__onBalanceUpdated),
         ('stats.crystal', self.__onBalanceUpdated),
         ('stats.freeXP', self.__onBalanceUpdated))

    def _getEvents(self):
        return ((self.__wallet.onWalletStatusChanged, self.__onWalletChanged),)

    def __updateCurrencies(self):
        with self.viewModel.transaction() as model:
            model.setIsWalletAvailable(self.__wallet.isAvailable)
            currencies = model.getCurrencies()
            currencies.clear()
            for tooltipId, currencyType in enumerate(CurrencyType, 1):
                amount = getCurrencyValueFromType(currencyType)
                resourceModel = CurrencyModel()
                resourceModel.setCurrencyType(currencyType)
                resourceModel.setValue(amount)
                self.__tooltipData[tooltipId] = _CURRENCY_TOOLTIPS.get(currencyType)
                resourceModel.setTooltipId(tooltipId)
                currencies.addViewModel(resourceModel)

            currencies.invalidate()

    def __onBalanceUpdated(self, *args, **kwargs):
        self.__updateCurrencies()

    def __onWalletChanged(self, _):
        self.viewModel.setIsWalletAvailable(self.__wallet.isAvailable)

    def createToolTip(self, event):
        contentID = event.contentID
        if contentID in self.__tooltipData.keys():
            toolTipData = createTooltipData(isSpecial=True, specialAlias=self.__tooltipData.get(contentID))
            if not toolTipData:
                _logger.warning('TooltipData not found for %s', self.__tooltipData.get(contentID))
                return super(CurrenciesTabView, self).createToolTipContent(event, contentID)
            window = BackportTooltipWindow(toolTipData, self.parentView.getParentWindow())
            window.load()
            return window
        return super(CurrenciesTabView, self).createToolTipContent(event, contentID)
