# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/dialogs/sub_views/top_right/br_money_balance.py
from battle_royale.gui.impl.dialogs import CurrencyTypeExtended
from gui.impl.dialogs.dialog_template_tooltip import DialogTemplateTooltip
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_royale.dialogs.sub_views.br_money_balance_view_model import BrMoneyBalanceViewModel
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleRentVehiclesController

class BRMoneyBalance(MoneyBalance):
    __rentVehiclesController = dependency.descriptor(IBattleRoyaleRentVehiclesController)

    def __init__(self):
        super(BRMoneyBalance, self).__init__(R.views.dialogs.sub_views.topRight.BRMoneyBalance(), BrMoneyBalanceViewModel())

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
            currency = event.getArgument('currency')
            factory = self._tooltips.get(CurrencyTypeExtended(currency))
            if factory and factory.tooltipFactory is not None:
                return factory.tooltipFactory()
        return super(BRMoneyBalance, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(BRMoneyBalance, self)._onLoading(*args, **kwargs)
        self.__rentVehiclesController.onBalanceUpdated += self.__onBalanceUpdated

    def _finalize(self):
        self.__rentVehiclesController.onBalanceUpdated -= self.__onBalanceUpdated
        super(BRMoneyBalance, self)._finalize()

    def _initTooltips(self):
        model = self.viewModel
        return {CurrencyTypeExtended.CREDITS: DialogTemplateTooltip(viewModel=model.creditsTooltip),
         CurrencyTypeExtended.BR_COIN: DialogTemplateTooltip(viewModel=model.brcoinsTooltip)}

    def _updateModel(self, model):
        isWGMAvailable = self._stats.mayConsumeWalletResources
        model.setIsWGMAvailable(isWGMAvailable)
        model.setCredits(int(self._stats.money.getSignValue(Currency.CREDITS)))
        brCoin = self.__rentVehiclesController.getBRCoinBalance(0)
        model.setBrcoins(brCoin)

    def __onBalanceUpdated(self):
        self._moneyChangeHandler()
