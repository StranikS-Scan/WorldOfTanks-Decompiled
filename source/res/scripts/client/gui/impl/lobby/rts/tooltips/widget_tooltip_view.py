# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/tooltips/widget_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.rts.tooltips.widget_tooltip_view_model import WidgetTooltipViewModel
from gui.impl.pub import ViewImpl
from helpers import dependency, time_utils
from skeletons.gui.game_control import IRTSProgressionController, IRTSBattlesController

class WidgetTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.rts.tooltips.WidgetTooltipView())
        settings.model = WidgetTooltipViewModel()
        super(WidgetTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WidgetTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        progressionCtrl = dependency.instance(IRTSProgressionController)
        currentProgress = progressionCtrl.getCollectionProgress()
        totalProgress = progressionCtrl.getCollectionSize()
        rtsBattlesController = dependency.instance(IRTSBattlesController)
        currentSeason = rtsBattlesController.getCurrentSeason()
        currentTime = time_utils.getCurrentLocalServerTimestamp()
        timeToEnd = 0
        timeToActive = 0
        if currentSeason:
            lastCycle = currentSeason.getLastCycleInfo()
            timeToEnd = lastCycle.endDate - currentTime
            currentCycle = currentSeason.getCycleInfo()
            if not currentCycle:
                nextCycle = currentSeason.getNextByTimeCycle(currentTime)
                if nextCycle:
                    timeToActive = nextCycle.startDate - currentTime
        with self.viewModel.transaction() as model:
            model.setCurrent(currentProgress)
            model.setTotal(totalProgress)
            model.setTimeToEnd(timeToEnd)
            model.setTimeToActive(timeToActive)
