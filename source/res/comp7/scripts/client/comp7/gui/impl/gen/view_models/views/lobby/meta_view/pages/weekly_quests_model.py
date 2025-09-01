# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/meta_view/pages/weekly_quests_model.py
from enum import IntEnum
from frameworks.wulf import Array, ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.progress_points_model import ProgressPointsModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.quest_card_model import QuestCardModel

class ChoiceRewardState(IntEnum):
    DEFAULT = 0
    ACTIVE = 1
    CLAIMED = 2


class WeeklyQuestsModel(ViewModel):
    __slots__ = ('onAnimationStart', 'onAnimationEnd', 'onGoToRewardsSelection')
    QUESTS_PER_WEEK = 5

    def __init__(self, properties=6, commands=3):
        super(WeeklyQuestsModel, self).__init__(properties=properties, commands=commands)

    def getTimeToNewQuests(self):
        return self._getNumber(0)

    def setTimeToNewQuests(self, value):
        self._setNumber(0, value)

    def getQuestCards(self):
        return self._getArray(1)

    def setQuestCards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getQuestCardsType():
        return QuestCardModel

    def getQuestsPassed(self):
        return self._getNumber(2)

    def setQuestsPassed(self, value):
        self._setNumber(2, value)

    def getPreviousQuestsPassed(self):
        return self._getNumber(3)

    def setPreviousQuestsPassed(self, value):
        self._setNumber(3, value)

    def getProgressPoints(self):
        return self._getArray(4)

    def setProgressPoints(self, value):
        self._setArray(4, value)

    @staticmethod
    def getProgressPointsType():
        return ProgressPointsModel

    def getChoiceRewardState(self):
        return ChoiceRewardState(self._getNumber(5))

    def setChoiceRewardState(self, value):
        self._setNumber(5, value.value)

    def _initialize(self):
        super(WeeklyQuestsModel, self)._initialize()
        self._addNumberProperty('timeToNewQuests', 0)
        self._addArrayProperty('questCards', Array())
        self._addNumberProperty('questsPassed', 0)
        self._addNumberProperty('previousQuestsPassed', 0)
        self._addArrayProperty('progressPoints', Array())
        self._addNumberProperty('choiceRewardState')
        self.onAnimationStart = self._addCommand('onAnimationStart')
        self.onAnimationEnd = self._addCommand('onAnimationEnd')
        self.onGoToRewardsSelection = self._addCommand('onGoToRewardsSelection')
