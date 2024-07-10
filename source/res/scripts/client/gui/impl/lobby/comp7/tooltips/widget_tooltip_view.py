# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/tooltips/widget_tooltip_view.py
from comp7_light_progression.skeletons.game_controller import IComp7LightProgressionOnTokensController
from gui.impl.gen.view_models.views.lobby.comp7.tooltips.widget_tooltip_view_model import ProgressionState, WidgetTooltipViewModel
from helpers import dependency
from helpers import time_utils
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from frameworks.wulf import ViewSettings, Array
from skeletons.gui.game_control import IComp7Controller
from skeletons.connection_mgr import IConnectionManager

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
    _comp7LightController = dependency.descriptor(IComp7Controller)
    _comp7LightProgression = dependency.descriptor(IComp7LightProgressionOnTokensController)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.comp7.tooltips.WidgetTooltipView())
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
            tx.setProgressionState(self.__getProgressionState())

    def __getTimeLeft(self):
        timeLeft = 0
        endDate, isActive = self._comp7LightController.getCurrentCycleInfo()
        if isActive:
            timeLeft = time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(endDate))
        return timeLeft

    def __getProgressionState(self):
        isInProgress = not self._comp7LightProgression.isFinished
        return ProgressionState.IN_PROGRESS if isInProgress else ProgressionState.COMPLETED
