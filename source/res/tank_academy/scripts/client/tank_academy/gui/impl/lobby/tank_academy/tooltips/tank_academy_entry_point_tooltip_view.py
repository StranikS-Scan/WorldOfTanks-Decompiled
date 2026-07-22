# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/lobby/tank_academy/tooltips/tank_academy_entry_point_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import ITankAcademyController
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy import tank_academy_entry_point_tooltip_view_model as ta_vm
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.quest_view_model import State
from tank_academy.gui.shared.bonus_packers import packBonusModelAndTooltipData

class TankAcademyEntryPointTooltipView(ViewImpl):
    __slots__ = ()
    __tankAcademyController = dependency.descriptor(ITankAcademyController)

    def __init__(self):
        settings = ViewSettings(R.views.tank_academy.lobby.tank_academy.tooltips.TankAcademyEntryPointTooltipView())
        settings.model = ta_vm.TankAcademyEntryPointTooltipViewModel()
        super(TankAcademyEntryPointTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TankAcademyEntryPointTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(TankAcademyEntryPointTooltipView, self)._onLoading()
        with self.viewModel.transaction() as model:
            totalQuestsCount = self.__tankAcademyController.getCountTankAcademyQuests()
            completedQuestsCount = self.__tankAcademyController.getCompletedTankAcademyQuestsCount()
            model.questProgress.setTotalQuests(totalQuestsCount)
            model.questProgress.setCountCompleted(completedQuestsCount)
            currentQuest = self.__tankAcademyController.getCurrentQuest()
            if currentQuest is not None:
                model.quest.setNumber(currentQuest.getOrder())
                model.quest.setTitle(currentQuest.getUserName())
                model.quest.setDescription(currentQuest.getDescription())
                model.quest.setCondition(currentQuest.getConditionLbl())
                model.quest.setState(State.DONE if currentQuest.isCompleted() else State.INPROGRESS)
                currentProgress, maxProgress = self.__tankAcademyController.getQuestProgress(currentQuest)
                model.quest.setCurrentProgress(currentProgress)
                model.quest.setMaxProgress(maxProgress)
                packBonusModelAndTooltipData(currentQuest.getBonuses(), model.quest.getRewards(), tooltipData=None)
            model.setHasToken(self.__tankAcademyController.hasUnobtainedDelayedRewards())
            if self.__tankAcademyController.isFinished() and self.__tankAcademyController.hasUnobtainedDelayedRewards():
                model.setEndDate(self.__tankAcademyController.getDelayedRewardExpirationTime())
        return
