# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_event_header_widget_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_event_header_widget_tooltip_view_model import WtEventHeaderWidgetTooltipViewModel, PerformanceRisk
from gui.impl.pub import ViewImpl
from gui.wt_event.wt_event_helpers import getSecondsLeft
from gui.wt_event.wt_event_bonuses_packers import getWtHiddenCustomizationIconUIPacker
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
        stageFinished = self.__gameEventCtrl.getFinishedLevelsCount()
        stageMax = self.__gameEventCtrl.getTotalLevelsCount()
        isCompleted = stageFinished == stageMax
        stageCurrent = self.__gameEventCtrl.getCurrentLevel()
        stampCountPerStage = self.__gameEventCtrl.getStampsCountPerLevel()
        stampsCurrent = self.__gameEventCtrl.getCurrentStampsCount()
        stampsMax = self.__gameEventCtrl.getTotalStampsCount()
        stampsForCurrentStage = stampCountPerStage * stageCurrent
        performanceRisk = self.__gameEventCtrl.analyzeClientSystem()
        progression = self.__gameEventCtrl.getConfig().progression
        if not isCompleted:
            currentStageData = progression[stageFinished]
            rewards = self.__gameEventCtrl.getQuestRewards(currentStageData.get('quest', ''))
        with self.viewModel.transaction() as model:
            model.setTimeLeft(getSecondsLeft(gameEventController=self.__gameEventCtrl))
            model.setCommonTotal(stampsMax)
            model.setStageCurrent(stageCurrent)
            model.setIsProgressionCompleted(isCompleted)
            model.setCommonCurrent(stampsCurrent)
            model.setStampsCurrent(stampsCurrent)
            model.setStampsMax(stampsForCurrentStage)
            model.setPerformanceRisk(PerformanceRisk(performanceRisk))
            if not isCompleted:
                rewardsList = model.getRewards()
                rewardsList.clear()
                rewardsList.reserve(len(rewards))
                packBonusModelAndTooltipData(rewards, rewardsList, None, getWtHiddenCustomizationIconUIPacker())
                rewardsList.invalidate()
        return
