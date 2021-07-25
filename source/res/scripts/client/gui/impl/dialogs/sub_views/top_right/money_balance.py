# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/sub_views/top_right/money_balance.py
from functools import partial
import typing
from frameworks.wulf import ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.dialogs.dialog_template_tooltip import DialogTemplateTooltip
from gui.impl.dialogs.dialog_template_utils import getCurrencyTooltipAlias
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencyType
from gui.impl.gen.view_models.views.dialogs.sub_views.money_balance_view_model import MoneyBalanceViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.tooltip_window import SimpleTooltipContent
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from frameworks.wulf import View
NO_WGM_TOOLTIP_DATA = {CurrencyType.GOLD: {'header': R.strings.tooltips.header.buttons.gold.header(),
                     'body': R.strings.tooltips.wallet.not_available_gold.body()},
 CurrencyType.CREDITS: {'header': R.strings.tooltips.header.buttons.credits.header(),
                        'body': R.strings.tooltips.wallet.not_available_credits.body()},
 CurrencyType.CRYSTAL: {'header': R.strings.tooltips.header.buttons.crystal.header(),
                        'body': R.strings.tooltips.wallet.not_available_crystal.body()},
 CurrencyType.FREEXP: {'header': R.strings.tooltips.header.buttons.freeXP.header(),
                       'body': R.strings.tooltips.wallet.not_available_freexp.body()}}

class MoneyBalance(ViewImpl):
    __slots__ = ('_stats', '__tooltips')
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID=None):
        settings = ViewSettings(layoutID or R.views.dialogs.sub_views.topRight.MoneyBalance())
        model = settings.model = MoneyBalanceViewModel()
        super(MoneyBalance, self).__init__(settings)
        self._stats = self._itemsCache.items.stats
        self.__tooltips = {CurrencyType.GOLD: DialogTemplateTooltip(viewModel=model.goldTooltip),
         CurrencyType.CREDITS: DialogTemplateTooltip(viewModel=model.creditsTooltip),
         CurrencyType.CRYSTAL: DialogTemplateTooltip(viewModel=model.crystalsTooltip),
         CurrencyType.FREEXP: DialogTemplateTooltip(viewModel=model.freeExpTooltip)}

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
            currency = event.getArgument('currency')
            factory = self.__tooltips.get(CurrencyType(currency))
            if factory and factory.tooltipFactory is not None:
                return factory.tooltipFactory()
        return super(MoneyBalance, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(MoneyBalance, self)._onLoading(*args, **kwargs)
        g_clientUpdateManager.addMoneyCallback(self._moneyChangeHandler)
        self.__setStats(self.viewModel)

    def _finalize(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        for tooltip in self.__tooltips.values():
            tooltip.dispose()

        super(MoneyBalance, self)._finalize()

    def _moneyChangeHandler(self, *_):
        with self.viewModel.transaction() as model:
            self.__setStats(model)

    def __setStats(self, model):
        isWGMAvailable = self._stats.mayConsumeWalletResources
        model.setIsWGMAvailable(isWGMAvailable)
        model.setCredits(int(self._stats.money.getSignValue(Currency.CREDITS)))
        model.setGold(int(self._stats.money.getSignValue(Currency.GOLD)))
        model.setCrystals(int(self._stats.money.getSignValue(Currency.CRYSTAL)))
        model.setFreeExp(self._stats.freeXP)
        for currency, tooltip in self.__tooltips.items():
            tooltip.isBackportTooltip = isWGMAvailable
            tooltip.tooltipFactory = partial(self.__WGMAvailableTooltipFactory if isWGMAvailable else self.__WGMNotAvailableTooltipFactory, currency)

    @staticmethod
    def __WGMAvailableTooltipFactory(currency):
        return createBackportTooltipContent(isSpecial=True, specialAlias=getCurrencyTooltipAlias(currency.value))

    @staticmethod
    def __WGMNotAvailableTooltipFactory(currency):
        params = NO_WGM_TOOLTIP_DATA.get(currency, {'header': '',
         'body': ''})
        return SimpleTooltipContent(R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent(), header=backport.text(params['header']), body=backport.text(params['body']))
