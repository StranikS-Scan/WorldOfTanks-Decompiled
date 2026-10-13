# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/tooltips/fort_rush_progression_tooltip.py
from __future__ import absolute_import
from fort_rush.gui.impl.gen.view_models.tooltips.fort_rush_progression_tooltip_view_model import FortRushProgressionTooltipViewModel
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.pub import ViewImpl
from gui.shared.missions.packers.bonus import getDefaultBonusPacker
from helpers import dependency

class FortRushProgressionWidgetTooltipView(ViewImpl):
    __ctrl = dependency.descriptor(IFortRushBattleController)

    def __init__(self):
        settings = ViewSettings(R.views.fort_rush.mono.lobby.tooltips.progression_widget_tooltip())
        settings.model = FortRushProgressionTooltipViewModel()
        super(FortRushProgressionWidgetTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(FortRushProgressionWidgetTooltipView, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    def __updateViewModel(self):
        isProgressionCompleted = self.__ctrl.isProgressionCompleted()
        with self.viewModel.transaction() as model:
            model.setIsAvailable(not self.__ctrl.isFrozen())
            model.setNewMissionsDateTime(self.__ctrl.getNewDailyMissionsTimestamp())
            model.setIsProgressionCompleted(isProgressionCompleted)
            if not isProgressionCompleted:
                currentPoints, stageTotal = self.__ctrl.getCurrentStagePoints()
                model.setCurrentProgressionPoints(currentPoints)
                model.setTotalProgressionPoints(stageTotal)
                model.setCurrentProgressionStage(self.__ctrl.getCurrentStageIndex())
                rewards = self.__ctrl.getCurrentProgressionStageRewards()
                rewardsArray = model.getRewards()
                rewardsArray.clear()
                bonusPacker = getDefaultBonusPacker()
                packBonusModelAndTooltipData(rewards, rewardsArray, None, bonusPacker)
                rewardsArray.invalidate()
        return
