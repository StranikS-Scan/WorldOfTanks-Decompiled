# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/weekly_quest_tooltip.py
from comp7.gui.impl.gen.view_models.views.lobby.missions.comp7_widget_quest_model import State as WidgetState
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.weekly_quest_tooltip_model import WeeklyQuestTooltipModel
from comp7.gui.impl.lobby.comp7_helpers.comp7_bonus_packer import getComp7BonusPacker, packQuestBonuses
from comp7.gui.shared.missions.packers.events import Comp7WeeklyQuestPacker
from comp7.skeletons.gui.game_control import IComp7WeeklyQuestsController
from frameworks.wulf import ViewSettings
from frameworks.wulf.view.array import fillViewModelsArray, fillIntsArray
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency

class WeeklyQuestTooltip(ViewImpl):
    __comp7WeeklyQuestsCtrl = dependency.descriptor(IComp7WeeklyQuestsController)

    def __init__(self):
        settings = ViewSettings(R.views.comp7.lobby.tooltips.WeeklyQuestTooltip())
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
