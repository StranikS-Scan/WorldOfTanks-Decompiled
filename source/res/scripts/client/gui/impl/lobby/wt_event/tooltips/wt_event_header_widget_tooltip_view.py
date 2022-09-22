# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_event_header_widget_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_event_header_widget_tooltip_view_model import WtEventHeaderWidgetTooltipViewModel, PerformanceRisk
from gui.impl.pub import ViewImpl
from gui.wt_event.wt_event_helpers import getDaysLeftFormatted
from helpers import dependency
from skeletons.gui.game_control import IEventBattlesController

class WtEventHeaderWidgetTooltipView(ViewImpl):
    __gameEventCtrl = dependency.descriptor(IEventBattlesController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.wt_event.tooltips.WtEventHeaderWidgetTooltipView())
        settings.model = WtEventHeaderWidgetTooltipViewModel()
        super(WtEventHeaderWidgetTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventHeaderWidgetTooltipView, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        super(WtEventHeaderWidgetTooltipView, self)._finalize()

    def __addListeners(self):
        self.__gameEventCtrl.onProgressUpdated += self.__updateViewModel

    def __removeListeners(self):
        self.__gameEventCtrl.onProgressUpdated -= self.__updateViewModel

    def __updateViewModel(self):
        currentProgress = self.__gameEventCtrl.getFinishedLevelsCount()
        totalProgress = self.__gameEventCtrl.getTotalLevelsCount()
        stampCountPerStage = self.__gameEventCtrl.getStampsCountPerLevel()
        completedStagesStampCount = self.__gameEventCtrl.getFinishedLevelsCount() * stampCountPerStage
        currentStageStampProgress = self.__gameEventCtrl.getCurrentStampsCount() - completedStagesStampCount
        stampsForNextStage = stampCountPerStage - currentStageStampProgress
        performanceRisk = self.__gameEventCtrl.analyzeClientSystem()
        with self.viewModel.transaction() as model:
            model.setCommonCurrent(currentProgress)
            model.setCommonTotal(totalProgress)
            model.setStampsForNextStage(stampsForNextStage)
            model.setDaysLeft(getDaysLeftFormatted(gameEventController=self.__gameEventCtrl))
            model.setPerformanceRisk(PerformanceRisk(performanceRisk))