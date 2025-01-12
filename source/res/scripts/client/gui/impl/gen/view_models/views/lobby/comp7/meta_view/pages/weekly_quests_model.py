# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/pages/weekly_quests_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.progress_points_model import ProgressPointsModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.quest_card_model import QuestCardModel

class WeeklyQuestsModel(ViewModel):
    __slots__ = ('onAnimationStart', 'onAnimationEnd')
    QUESTS_PER_WEEK = 5

    def __init__(self, properties=5, commands=2):
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

    def _initialize(self):
        super(WeeklyQuestsModel, self)._initialize()
        self._addNumberProperty('timeToNewQuests', 0)
        self._addArrayProperty('questCards', Array())
        self._addNumberProperty('questsPassed', 0)
        self._addNumberProperty('previousQuestsPassed', 0)
        self._addArrayProperty('progressPoints', Array())
        self.onAnimationStart = self._addCommand('onAnimationStart')
        self.onAnimationEnd = self._addCommand('onAnimationEnd')
