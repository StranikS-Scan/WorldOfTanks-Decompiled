# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/hb_progression_widget_tooltip.py
from frameworks.wulf import ViewSettings
from helpers import dependency
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.hb_progression_widget_tooltip_model import HbProgressionWidgetTooltipModel
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from historical_battles.gui.impl.lobby.views.bonus_packer import getBonusPacker

class HbProgressionWidgetTooltip(ViewImpl):
    __slots__ = ()
    __gameEventController = dependency.descriptor(IGameEventController)
    __hbProgressionController = dependency.descriptor(IHBProgressionOnTokensController)

    def __init__(self):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.ProgressionWidgetTooltip())
        settings.model = HbProgressionWidgetTooltipModel()
        super(HbProgressionWidgetTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(HbProgressionWidgetTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.__fillModel()

    def __fillModel(self):
        currentFront = self.__gameEventController.frontController.getSelectedFront()
        stageData = self.__hbProgressionController.getCurrentStageAbsoluteData()
        curStage = stageData.get('currentStage')
        with self.getViewModel().transaction() as model:
            model.setFrontName(currentFront.getName())
            model.setLevel(curStage)
            model.setCurrentPoints(stageData.get('currentPoints'))
            model.setMaxLevelPoints(stageData.get('stageMaxPoints'))
            model.setMinLevelPoints(stageData.get('stageMinPoints'))
            self.__fillRewards(model, curStage)

    def __fillRewards(self, model, currentStage):
        rewardsModel = model.getRewards()
        rewardsModel.clear()
        lvlData = self.__hbProgressionController.getProgressionLevelsData()[currentStage - 1]
        bonuses = lvlData['rewards']
        packBonusModelAndTooltipData(bonuses, rewardsModel, packer=getBonusPacker())
        rewardsModel.invalidate()
