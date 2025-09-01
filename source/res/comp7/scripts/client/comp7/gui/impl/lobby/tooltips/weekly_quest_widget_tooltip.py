# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/weekly_quest_widget_tooltip.py
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.weekly_quest_widget_tooltip_model import WeeklyQuestWidgetTooltipModel, State
from comp7.gui.impl.lobby.comp7_helpers.comp7_bonus_packer import getComp7BonusPacker, packQuestBonuses
from comp7.gui.shared.missions.packers.events import Comp7WeeklyQuestPacker
from comp7.skeletons.gui.game_control import IComp7WeeklyQuestsController
from frameworks.wulf import ViewSettings
from frameworks.wulf.view.array import fillViewModelsArray, fillIntsArray
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency

class WeeklyQuestWidgetTooltip(ViewImpl):
    __comp7WeeklyQuestsCtrl = dependency.descriptor(IComp7WeeklyQuestsController)

    def __init__(self):
        settings = ViewSettings(R.views.comp7.mono.lobby.tooltips.weekly_quest_widget_tooltip())
        settings.model = WeeklyQuestWidgetTooltipModel()
        super(WeeklyQuestWidgetTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WeeklyQuestWidgetTooltip, self).getViewModel()

    def _onLoading(self):
        super(WeeklyQuestWidgetTooltip, self)._onLoading()
        self.__updateModel()

    def __updateModel(self):
        with self.viewModel.transaction() as vm:
            quests = self.__comp7WeeklyQuestsCtrl.getQuests()
            vm.setQuestsPassed(quests.numCompletedBattleQuests)
            vm.setTotalQuests(quests.numBattleQuests)
            vm.setTimeToNewQuests(quests.getTimeToNewQuests())
            vm.setState(self.__getQuestsState())
            bonusPacker = getComp7BonusPacker()
            if quests.newQuest:
                packedBonuses, _ = packQuestBonuses(quests.newQuest.getBonuses(), bonusPacker)
            else:
                packedBonuses = []
            questPacker = Comp7WeeklyQuestPacker()
            _, _, _, description = questPacker.getData(quests.newQuest)
            vm.setDescription(description)
            fillViewModelsArray(packedBonuses, self.viewModel.getBonuses())
            fillIntsArray(quests.numBattleQuestsToCompleteByTokenQuestIdx, vm.getQuestNumbersToRewards())

    def __getQuestsState(self):
        weeklyQuests = self.__comp7WeeklyQuestsCtrl.getQuests()
        if weeklyQuests.numBattleQuests == weeklyQuests.numCompletedBattleQuests:
            return State.REWARD
        return State.ACTIVE if weeklyQuests.newQuest.isStarted() else State.WAITING
