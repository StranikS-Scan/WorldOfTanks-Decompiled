# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/battle_mode_info_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from helpers import dependency, time_utils
from historical_battles.gui.impl.gen.view_models.views.lobby.battle_mode_model import FrontStateType
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.battle_mode_info_tooltip_model import BattleModeInfoTooltipModel
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache

class BattleModeInfoTooltip(ViewImpl):
    __slots__ = ('__frontName',)
    _gameEventController = dependency.descriptor(IGameEventController)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, frontName):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.BattleModeInfoTooltip())
        settings.model = BattleModeInfoTooltipModel()
        self.__frontName = frontName
        super(BattleModeInfoTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleModeInfoTooltip, self).getViewModel()

    def _onLoading(self):
        super(BattleModeInfoTooltip, self)._initialize()
        front = self._gameEventController.frontController.getFrontByName(self.__frontName)
        if front is None:
            return
        else:
            with self.viewModel.transaction() as tx:
                startTimeLeft = time_utils.getTimeDeltaFromNow(front.getStartTime())
                tx.setFrontState(FrontStateType.SOON)
                if front.isEnabled():
                    tx.setFrontState(FrontStateType.AVAILABLE if startTimeLeft <= 0 else FrontStateType.COUNTDOWN)
                tx.setFrontName(front.getName())
                tx.setCountDownSeconds(startTimeLeft)
                tx.setFrontStartTimestamp(front.getStartTime())
                tx.setEventEndTimestamp(self._gameEventController.getEventFinishTime())
                tx.earnings.setType(front.getCoinsName())
            return
