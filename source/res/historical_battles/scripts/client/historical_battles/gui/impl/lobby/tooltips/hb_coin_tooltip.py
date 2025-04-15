# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/hb_coin_tooltip.py
from frameworks.wulf import ViewSettings
from helpers import dependency
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.hb_coin_tooltip_model import HbCoinTooltipModel

class HbCoinTooltip(ViewImpl):
    __slots__ = ()
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, coinType=None):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.HbCoinTooltip())
        settings.model = HbCoinTooltipModel()
        if coinType is None:
            coinType = self.__gameEventController.frontController.getSelectedFront().getCoinsName()
            if coinType is None:
                raise ValueError('No coin type provided and no selected front available.')
        playerCoinAmount = self.__gameEventController.coins.getCount(coinType)
        settings.model.coin.setAmount(playerCoinAmount)
        settings.model.coin.setType(coinType)
        settings.model.setFrontName(coinType)
        super(HbCoinTooltip, self).__init__(settings)
        return
