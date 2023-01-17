# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/collective_goal/tooltips/entry_point_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.collective_goal.tooltips.collective_goal_entry_tooltip_model import CollectiveGoalEntryTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency
from skeletons.gui.game_control import ICollectiveGoalEntryPointController

class EntryPointTooltip(ViewImpl):
    __slots__ = ()
    __collectiveGoalEntryPointController = dependency.descriptor(ICollectiveGoalEntryPointController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.collective_goal.tooltips.EntryPointTooltip())
        settings.model = CollectiveGoalEntryTooltipModel()
        super(EntryPointTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryPointTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EntryPointTooltip, self)._onLoading()
        with self.viewModel.transaction() as model:
            self.__fillInfo(model=model)

    @replaceNoneKwargsModel
    def __fillInfo(self, model=None):
        stage, _ = self.__collectiveGoalEntryPointController.getCurrentDiscount()
        model.setStage(stage)
        model.setIcon(self.__collectiveGoalEntryPointController.getGoalType())
        model.setTitle(self.__collectiveGoalEntryPointController.getMarathonName())
        model.setDescription(self.__collectiveGoalEntryPointController.getGoalDescription())
        model.setCaption(self.__collectiveGoalEntryPointController.getRulesCaption())
        currentPoints, totalPoints = self.__collectiveGoalEntryPointController.getStagePoints()
        model.setCurrentPoints(min(currentPoints, totalPoints))
        model.setTotalPoints(totalPoints)
        model.setEndDate(self.__collectiveGoalEntryPointController.getEventFinishTime())
        model.setIsFinished(self.__collectiveGoalEntryPointController.isFinished())
