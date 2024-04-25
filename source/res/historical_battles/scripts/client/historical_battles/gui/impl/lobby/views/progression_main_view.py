# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/views/progression_main_view.py
import logging
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.lobby.progression.progression_main_view_model import ProgressionMainViewModel, MainViews
from historical_battles.gui.impl.lobby.tooltips.hb_special_vehicles_tooltip import HBSpecialVehiclesTooltip
from historical_battles.gui.impl.lobby.tooltips.hb_vehicle_reward_tooltip import HBVehicleRewardTooltip
from historical_battles.gui.impl.lobby.tooltips.hb_coin_tooltip import HbCoinTooltip
from historical_battles.gui.impl.lobby.views.progression_view import ProgressionView
from historical_battles.gui.impl.lobby.base_event_view import BaseEventView
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
_logger = logging.getLogger(__name__)

class ProgressionMainView(BaseEventView):
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.historical_battles.lobby.ProgressionMainView())
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = ProgressionMainViewModel()
        super(ProgressionMainView, self).__init__(settings)
        self.__progressionView = None
        self.__tooltipEnabled = True
        return

    @property
    def viewModel(self):
        return super(ProgressionMainView, self).getViewModel()

    @property
    def currentPresenter(self):
        return self.__progressionView

    def createToolTip(self, event):
        return self.__progressionView.createToolTip(event) or super(ProgressionMainView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.historical_battles.lobby.tooltips.HbCoinTooltip():
            coinType = event.getArgument('coinType')
            if coinType is None:
                _logger.error('HbCoinTooltip must receive a viable coinType param. Received: None')
                return
            return HbCoinTooltip(coinType)
        elif contentID == R.views.historical_battles.lobby.tooltips.HbSpecialVehiclesTooltip():
            return HBSpecialVehiclesTooltip()
        else:
            return HBVehicleRewardTooltip() if contentID == R.views.historical_battles.lobby.tooltips.HbVehicleRewardTooltip() else None

    def _onLoading(self, *args, **kwargs):
        super(ProgressionMainView, self)._onLoading(args, kwargs)
        self._gameEventController.setShowingProgressionView(True)
        self.__progressionView = ProgressionView(self.viewModel.progressionModel, self)
        if self.__progressionView is None:
            return
        else:
            self.__progressionView.finalize()
            with self.viewModel.transaction() as tx:
                self.__progressionView.initialize(MainViews.PROGRESSION)
                tx.setViewType(MainViews.PROGRESSION)
            soundCtrl = self._gameEventController.soundProgressionCtrl
            if soundCtrl:
                soundCtrl.onHBProgressionViewLoaded()
            return

    def _finalize(self):
        self._gameEventController.setShowingProgressionView(False)
        if self.__progressionView is not None:
            self.__progressionView.finalize()
        self.__progressionView = None
        soundCtrl = self._gameEventController.soundProgressionCtrl
        if soundCtrl:
            soundCtrl.onHBProgressionLeave()
        super(ProgressionMainView, self)._finalize()
        return
