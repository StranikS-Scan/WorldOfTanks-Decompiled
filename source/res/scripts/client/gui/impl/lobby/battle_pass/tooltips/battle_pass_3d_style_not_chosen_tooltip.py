# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_pass_3d_style_not_chosen_tooltip.py
from frameworks.wulf import ViewSettings
from gui.battle_pass.battle_pass_helpers import getNotChosen3DStylesCount
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_pass_3d_style_not_chosen_tooltip_model import BattlePass3DStyleNotChosenTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController

class BattlePass3dStyleNotChosenTooltip(ViewImpl):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.BattlePass3dStyleNotChosenTooltip())
        settings.model = BattlePass3DStyleNotChosenTooltipModel()
        super(BattlePass3dStyleNotChosenTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePass3dStyleNotChosenTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattlePass3dStyleNotChosenTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setLevel(min(self.__battlePassController.getCurrentLevel() + 1, self.__battlePassController.getMaxLevel()))
            currentChapter = self.__battlePassController.getCurrentChapter()
            model.setChapter(currentChapter)
            if currentChapter > 1:
                firstNotChosenStyleChapter = getNotChosen3DStylesCount(battlePass=self.__battlePassController) + 1 - currentChapter
                if firstNotChosenStyleChapter < currentChapter:
                    model.setIsChapterCompleted(True)
