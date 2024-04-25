# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/widgets/coin_widget.py
from gui.prb_control import prbDispatcherProperty
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.common.coin_exchange_widget_model import CoinExchangeWidgetModel
from historical_battles.gui.impl.gen.view_models.views.common.hb_coin_model import HbCoinModel
from historical_battles.gui.shared.event_dispatcher import showCoinsExchangeWindow
from historical_battles.skeletons.gui.game_event_controller import IGameEventController

class CoinWidget(object):
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, viewModel):
        self.__viewModel = viewModel

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def onLoading(self):
        self._gameEventController.coins.onCoinsCountChanged += self.__onCoinsCountChanged
        if self.__viewModel:
            self.__viewModel.onExchangeClick += self.__onExchangeClick

    def destroy(self):
        coins = self._gameEventController.coins
        if coins:
            coins.onCoinsCountChanged -= self.__onCoinsCountChanged
        if self.__viewModel:
            self.__viewModel.onExchangeClick = self.__onExchangeClick

    def updateModel(self, model):
        earnings = model.getEarnings()
        unavailableExchangeCoins = 0
        disabledExchangeCoins = 0
        for front in self._gameEventController.frontController.getFronts().itervalues():
            coinName = front.getCoinsName()
            unavailableExchangeCoins += int(not self._gameEventController.coins.isExchangeStarted(coinName))
            disabledExchangeCoins += int(not self._gameEventController.coins.isExchangeEnabled(coinName))
            hbCoin = next((m for m in earnings if m.getType() == coinName), None)
            if hbCoin is None:
                hbCoin = HbCoinModel()
                hbCoin.setType(coinName)
                earnings.addViewModel(hbCoin)
            hbCoin.setAmount(self._gameEventController.coins.getCount(coinName))

        earnings.invalidate()
        if disabledExchangeCoins >= 2:
            model.setIsHardDisabled(True)
        elif unavailableExchangeCoins >= 2:
            model.setIsExchangeEnabled(False)
        elif disabledExchangeCoins + unavailableExchangeCoins >= 2:
            model.setIsHardDisabled(True)
        return

    def __onCoinsCountChanged(self, _):
        with self.__viewModel.transaction() as tx:
            self.updateModel(tx)

    def __onExchangeClick(self):
        showCoinsExchangeWindow()
