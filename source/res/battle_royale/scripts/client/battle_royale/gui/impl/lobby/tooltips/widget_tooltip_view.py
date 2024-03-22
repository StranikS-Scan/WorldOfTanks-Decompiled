# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/widget_tooltip_view.py
from battle_royale.gui.constants import BattleRoyalePerfProblems
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.widget_tooltip_view_model import PerformanceRisk, ProgressionState
from battle_royale.gui.shared.tooltips.helper import fillProgressionPointsTableModel
from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController
from helpers import dependency
from helpers import time_utils
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from frameworks.wulf import ViewSettings, Array
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.widget_tooltip_view_model import WidgetTooltipViewModel
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.connection_mgr import IConnectionManager
PERFORMANCE_RISK_MAPPING = {BattleRoyalePerfProblems.HIGH_RISK: PerformanceRisk.HIGH,
 BattleRoyalePerfProblems.MEDIUM_RISK: PerformanceRisk.MEDIUM,
 BattleRoyalePerfProblems.LOW_RISK: PerformanceRisk.LOW}

def packPeriods(periods):
    dayArray = Array()
    for periodStart, periodEnd in periods:
        periodsArray = Array()
        periodsArray.addNumber(int(periodStart))
        periodsArray.addNumber(int(periodEnd))
        dayArray.addArray(periodsArray)

    return dayArray


class WidgetTooltipView(ViewImpl):
    _connectionMgr = dependency.descriptor(IConnectionManager)
    _battleController = dependency.descriptor(IBattleRoyaleController)
    _brProgression = dependency.descriptor(IBRProgressionOnTokensController)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.battle_royale.lobby.tooltips.WidgetTooltipView())
        settings.model = WidgetTooltipViewModel()
        super(WidgetTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WidgetTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WidgetTooltipView, self)._onLoading(args, kwargs)
        self.__updateModel()

    def __updateModel(self):
        with self.viewModel.transaction() as tx:
            tx.setTime(self.__getTimeLeft())
            tx.setPerformance(PERFORMANCE_RISK_MAPPING[self._battleController.getPerformanceGroup()])
            tx.setProgressionState(self.__getProgressionState())
            self.__updatePeriods(tx.getBattleSchedule())
            fillProgressionPointsTableModel(tx.leaderBoard, self._battleController.getProgressionPointsTableData())

    def __updatePeriods(self, model):
        primeTime = self._battleController.getPrimeTimes().get(self._connectionMgr.peripheryID)
        currentCycleEnd = self._battleController.getCurrentSeason().getCycleEndDate()
        todayStart, todayEnd = time_utils.getDayTimeBoundsForLocal()
        todayEnd += 1
        tomorrowStart, tomorrowEnd = todayStart + time_utils.ONE_DAY, todayEnd + time_utils.ONE_DAY
        tomorrowEnd += 1
        todayPeriods = ()
        tomorrowPeriods = ()
        if primeTime is not None:
            todayPeriods = primeTime.getPeriodsBetween(todayStart, min(todayEnd, currentCycleEnd))
            if tomorrowStart < currentCycleEnd:
                tomorrowPeriods = primeTime.getPeriodsBetween(tomorrowStart, min(tomorrowEnd, currentCycleEnd))
        model.addArray(packPeriods(todayPeriods))
        model.addArray(packPeriods(tomorrowPeriods))
        return

    def __getTimeLeft(self):
        timeLeft = 0
        currentCycleInfo = self._battleController.getCurrentCycleInfo()
        if currentCycleInfo[1]:
            timeLeft = time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(currentCycleInfo[0]))
        return timeLeft

    def __getProgressionState(self):
        isEnabled = self._brProgression.isEnabled
        if not isEnabled:
            return ProgressionState.UNAVAILABLE
        isInProgress = not self._brProgression.isFinished
        return ProgressionState.IN_PROGRESS if isInProgress else ProgressionState.COMPLETED
