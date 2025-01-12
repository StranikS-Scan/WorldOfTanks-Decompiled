# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/tooltips/weekly_quest_tooltip.py
from frameworks.wulf import ViewSettings
from frameworks.wulf.view.array import fillViewModelsArray, fillIntsArray
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.tooltips.weekly_quest_tooltip_model import WeeklyQuestTooltipModel
from gui.impl.gen.view_models.views.lobby.missions.widget.comp7_daily_quest_model import State as WidgetState
from gui.impl.lobby.comp7.comp7_bonus_packer import packQuestBonuses, getComp7BonusPacker
from gui.impl.pub import ViewImpl
from gui.shared.missions.packers.events import Comp7WeeklyQuestPacker
from helpers import dependency
from skeletons.gui.game_control import IComp7WeeklyQuestsController

class WeeklyQuestTooltip(ViewImpl):
    __comp7WeeklyQuestsCtrl = dependency.descriptor(IComp7WeeklyQuestsController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.comp7.tooltips.WeeklyQuestTooltip())
        settings.model = WeeklyQuestTooltipModel()
        super(WeeklyQuestTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WeeklyQuestTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WeeklyQuestTooltip, self)._onLoading(args, kwargs)
        self.__updateComp7WeeklyQuestTooltip()
        self.__comp7WeeklyQuestsCtrl.onWeeklyQuestsUpdated += self.__onWeeklyQuestsUpdated

    def _finalize(self):
        super(WeeklyQuestTooltip, self)._finalize()
        self.__comp7WeeklyQuestsCtrl.onWeeklyQuestsUpdated -= self.__onWeeklyQuestsUpdated
        self.__questData = None
        return

    def __onWeeklyQuestsUpdated(self, _):
        self.__updateComp7WeeklyQuestTooltip()

    def __updateComp7WeeklyQuestTooltip(self):
        weeklyQuests = self.__comp7WeeklyQuestsCtrl.getQuests()
        state = weeklyQuests.newQuestState
        if state == WidgetState.HIDE:
            return
        with self.getViewModel().transaction() as model:
            model.setState(state)
            if state == WidgetState.REWARD:
                return
            quest = weeklyQuests.newQuest
            icon, currentProgress, totalProgress, description = Comp7WeeklyQuestPacker.getData(quest)
            model.setCurrentProgress(currentProgress)
            model.setTotalProgress(totalProgress)
            model.setTotalQuests(weeklyQuests.numBattleQuests)
            model.setQuestsPassed(weeklyQuests.numCompletedBattleQuests)
            model.setTimeToNewQuests(self.__comp7WeeklyQuestsCtrl.getQuests().getTimeToNewQuests())
            fillIntsArray(weeklyQuests.numBattleQuestsToCompleteByTokenQuestIdx, model.getQuestNumbersToRewards())
            if state == WidgetState.WAITING:
                return
            model.setDescription(description)
            model.setQuestType(icon)
            packedBonuses, _ = packQuestBonuses(quest.getBonuses(), getComp7BonusPacker())
            fillViewModelsArray(packedBonuses, model.getRewards())
