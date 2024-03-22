# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/br_money_balance.py
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_royale.dialogs.sub_views.br_money_balance_view_model import BrMoneyBalanceViewModel
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

class BRMoneyBalance(MoneyBalance):
    battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self):
        super(BRMoneyBalance, self).__init__(R.views.dialogs.sub_views.topRight.BRMoneyBalance(), BrMoneyBalanceViewModel())

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BRMoneyBalance, self)._onLoading(*args, **kwargs)
        self.battleRoyaleController.onBalanceUpdated += self.__onBalanceUpdated

    def _finalize(self):
        self.battleRoyaleController.onBalanceUpdated -= self.__onBalanceUpdated
        super(BRMoneyBalance, self)._finalize()

    def _updateModel(self, model):
        isWGMAvailable = self._stats.mayConsumeWalletResources
        model.setIsWGMAvailable(isWGMAvailable)
        model.setCredits(int(self._stats.money.getSignValue(Currency.CREDITS)))
        brCoin = self.battleRoyaleController.getBRCoinBalance(0)
        model.setBrcoins(brCoin)

    def __onBalanceUpdated(self):
        self._moneyChangeHandler()
