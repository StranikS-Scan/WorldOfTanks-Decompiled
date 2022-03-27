# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/tooltips/rts_points_tooltip_view.py
import logging
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.rts.tooltips.rts_points_condition_model import RtsPointsConditionModel
from gui.impl.gen.view_models.views.lobby.rts.tooltips.rts_points_tooltip_view_model import RtsPointsTooltipViewModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class RTSPointsTooltipViewBase(ViewImpl):
    __slots__ = ()
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.rts.tooltips.RTSPointsTooltipView())
        settings.model = RtsPointsTooltipViewModel()
        super(RTSPointsTooltipViewBase, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RTSPointsTooltipViewBase, self).getViewModel()

    def _getLeaderboard(self):
        return {}


class RTSPointsTooltipViewTanker(RTSPointsTooltipViewBase):

    def _getLeaderboard(self):
        return self._lobbyContext.getServerSettings().getRTSBattlesConfig().getLeaderboardTanker()

    def _onLoading(self, *args, **kwargs):
        leaderboard = self._getLeaderboard()
        with self.viewModel.transaction() as model:
            model.setIsStrategist(False)
            conditionRecords = model.getConditions()
            conditionRecords.clear()
            self._addRecords(leaderboard['win'], conditionRecords)
            self._addRecords(leaderboard['lose'], conditionRecords)
            conditionRecords.invalidate()

    def _addRecords(self, leaderboard, array):
        startRange = 1
        endRange = 0
        lastValue = None
        for it in leaderboard:
            if lastValue is not None and lastValue != it:
                self._addConditionRecordModel(array, lastValue, startRange, endRange)
                startRange = endRange + 1
            lastValue = it
            endRange += 1

        if lastValue is not None:
            self._addConditionRecordModel(array, lastValue, startRange, endRange)
        return

    def _addConditionRecordModel(self, array, point, start, end):
        conditionRecord = RtsPointsConditionModel()
        conditionRecord.setPlaceRange(str(start) + '-' + str(end))
        conditionRecord.setPoints(point)
        array.addViewModel(conditionRecord)


class RTSPointsTooltipView1x7(RTSPointsTooltipViewBase):

    def _getLeaderboard(self):
        return self._lobbyContext.getServerSettings().getRTSBattlesConfig().getLeaderboard1x7()

    def _onLoading(self, *args, **kwargs):
        leaderboard = self._getLeaderboard()
        with self.viewModel.transaction() as model:
            model.setIsStrategist(True)
            conditionRecords = model.getConditions()
            conditionRecords.clear()
            for condition in [{'points': leaderboard['win']}, {'points': leaderboard['lose']}]:
                conditionRecord = RtsPointsConditionModel()
                conditionRecord.setPoints(condition.get('points'))
                conditionRecords.addViewModel(conditionRecord)

            conditionRecords.invalidate()


class RTSPointsTooltipView1x1(RTSPointsTooltipView1x7):

    def _getLeaderboard(self):
        return self._lobbyContext.getServerSettings().getRTSBattlesConfig().getLeaderboard1x1()
