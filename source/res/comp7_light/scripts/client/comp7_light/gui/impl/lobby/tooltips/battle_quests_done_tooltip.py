# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/tooltips/battle_quests_done_tooltip.py
from comp7_core.gui.impl.lobby.comp7_core_helpers.comp7_core_model_helpers import setSeasonInfo
from comp7_light.gui.impl.gen.view_models.views.lobby.season_model import SeasonState as Comp7LightSeasonState
from comp7_light.gui.impl.gen.view_models.views.lobby.enums import SeasonName as Comp7LightSeasonName
from comp7_light.gui.impl.gen.view_models.views.lobby.tooltips.battle_quests_done_tooltip_model import BattleQuestsDoneTooltipModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.server_events.events_helpers import EventInfoModel
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import IComp7LightController

class BattleQuestsDoneTooltip(ViewImpl):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def __init__(self):
        settings = ViewSettings(R.views.comp7_light.mono.lobby.tooltips.all_quests_done_tooltip())
        settings.model = BattleQuestsDoneTooltipModel()
        super(BattleQuestsDoneTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleQuestsDoneTooltip, self).getViewModel()

    def _getEvents(self):
        return ((self.__comp7LightController.onStatusUpdated, self._onStatusUpdated), (self.__comp7LightController.onStatusTick, self._onStatusTick), (self.viewModel.season.pollServerTime, self.__onPollServerTime))

    def _onLoading(self, *args, **kwargs):
        self._updateState()
        super(BattleQuestsDoneTooltip, self)._onLoading()

    def _onStatusUpdated(self, _):
        self._updateState()

    def _onStatusTick(self):
        self._updateState()

    def _updateState(self):
        dailyResetTimeDelta = EventInfoModel.getDailyProgressResetTimeDelta()
        with self.viewModel.transaction() as vm:
            vm.setCountdown(dailyResetTimeDelta)
            season = self.__comp7LightController.getCurrentSeason() or self.__comp7LightController.getNextSeason() or self.__comp7LightController.getPreviousSeason()
            setSeasonInfo(vm.season, self.__comp7LightController, Comp7LightSeasonState, Comp7LightSeasonName, season)

    def __onPollServerTime(self):
        with self.viewModel.transaction() as tx:
            tx.season.setServerTimestamp(round(getServerUTCTime()))
