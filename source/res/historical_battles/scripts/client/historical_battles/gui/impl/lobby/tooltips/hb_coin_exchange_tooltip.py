# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/hb_coin_exchange_tooltip.py
from gui.impl.gen import R
from frameworks.wulf import ViewSettings
from helpers import dependency, time_utils
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.hb_coin_exchange_tooltip_model import HbCoinExchangeTooltipModel
from gui.impl.pub import ViewImpl
from historical_battles.skeletons.gui.game_event_controller import IGameEventController

class HbCoinExchangeTooltip(ViewImpl):
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.HbCoinExchangeTooltip())
        settings.model = HbCoinExchangeTooltipModel()
        super(HbCoinExchangeTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(HbCoinExchangeTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(HbCoinExchangeTooltip, self)._onLoading(*args, **kwargs)
        secondFront = self._gameEventController.frontController.getFrontByID(1)
        if not secondFront.isStarted():
            startTimer = max(0, int(time_utils.makeLocalServerTime(secondFront.getStartTime()) - time_utils.getCurrentTimestamp()))
            self.viewModel.setCountDownSeconds(startTimer)
