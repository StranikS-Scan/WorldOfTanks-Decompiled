# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/hb_coin_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.hb_coin_tooltip_model import HbCoinTooltipModel
from historical_battles.skeletons.gui.game_event_controller import IGameEventController

class HbCoinTooltip(ViewImpl):
    __slots__ = ()
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, coinType, itemPrice=None):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.HbCoinTooltip())
        settings.model = HbCoinTooltipModel()
        settings.model.coin.setType(coinType)
        playerCoinAmount = self._gameEventController.coins.getCount(coinType)
        if itemPrice:
            priceAmountDiff = playerCoinAmount - itemPrice
            if priceAmountDiff < 0:
                settings.model.setInsufficientCoins(-priceAmountDiff)
            else:
                settings.model.setInsufficientCoins(0)
        settings.model.coin.setAmount(playerCoinAmount)
        super(HbCoinTooltip, self).__init__(settings)
