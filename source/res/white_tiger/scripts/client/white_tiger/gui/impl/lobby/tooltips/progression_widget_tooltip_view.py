# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/progression_widget_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.hangar_progression_tooltip_view_model import HangarProgressionTooltipViewModel, PerformanceRisk
from white_tiger.gui.wt_event_helpers import getSecondsLeft
from white_tiger.skeletons.economics_controller import IEconomicsController
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from white_tiger.gui.wt_bonus_packers import getWTEventBonusPacker

class ProgressionWidgetTooltipView(ViewImpl):
    __economicsCtrl = dependency.descriptor(IEconomicsController)
    __whiteTigerCtrl = dependency.descriptor(IWhiteTigerController)

    def __init__(self):
        settings = ViewSettings(R.views.white_tiger.mono.lobby.tooltips.progression_widget_tooltip())
        settings.model = HangarProgressionTooltipViewModel()
        super(ProgressionWidgetTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ProgressionWidgetTooltipView, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    def __updateViewModel(self):
        stageFinished = self.__economicsCtrl.getFinishedLevelsCount()
        maxProgression = self.__economicsCtrl.getProgressionMaxLevel()
        currentLevel = self.__economicsCtrl.getCurrentLevel()
        currentStamps = self.__economicsCtrl.getStampsCount()
        isProgressionCompleted = stageFinished == maxProgression
        progression = self.__economicsCtrl.getConfig().get('progression', None)
        if not isProgressionCompleted and progression:
            currentStageData = progression[stageFinished]
            rewards = self.__economicsCtrl.getProgressionRewards(currentStageData.get('quest', ''))
        with self.viewModel.transaction() as model:
            model.setTimeLeft(getSecondsLeft(gameEventController=self.__whiteTigerCtrl))
            model.setCommonTotal(self.__economicsCtrl.getMaxRequiredStampsCount())
            model.setStageCurrent(currentLevel)
            model.setIsProgressionCompleted(isProgressionCompleted)
            model.setCommonCurrent(currentStamps)
            model.setStampsCurrent(currentStamps)
            model.setStampsMax(self.__economicsCtrl.getStampsCountPerLevel() * currentLevel)
            model.setPerformanceRisk(PerformanceRisk(self.__whiteTigerCtrl.analyzeClientSystem()))
            if not isProgressionCompleted:
                rewardsList = model.getRewards()
                rewardsList.clear()
                rewardsList.reserve(len(rewards))
                packBonusModelAndTooltipData(rewards, rewardsList, None, getWTEventBonusPacker())
                rewardsList.invalidate()
        return
