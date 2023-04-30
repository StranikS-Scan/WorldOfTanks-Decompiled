# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/pages/weekly_quests_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.progress_points_model import ProgressPointsModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.quest_card_model import QuestCardModel

class SeasonState(Enum):
    NOTSTARTED = 'notStarted'
    ACTIVE = 'active'
    LASTWEEK = 'lastWeek'
    FINISHED = 'finished'


class WeeklyQuestsModel(ViewModel):
    __slots__ = ('onAnimationStart', 'onAnimationEnd')

    def __init__(self, properties=6, commands=2):
        super(WeeklyQuestsModel, self).__init__(properties=properties, commands=commands)

    def getSeasonState(self):
        return SeasonState(self._getString(0))

    def setSeasonState(self, value):
        self._setString(0, value.value)

    def getResetTimeLeft(self):
        return self._getNumber(1)

    def setResetTimeLeft(self, value):
        self._setNumber(1, value)

    def getQuestCards(self):
        return self._getArray(2)

    def setQuestCards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getQuestCardsType():
        return QuestCardModel

    def getCurrentTokenValue(self):
        return self._getNumber(3)

    def setCurrentTokenValue(self, value):
        self._setNumber(3, value)

    def getPreviousTokenValue(self):
        return self._getNumber(4)

    def setPreviousTokenValue(self, value):
        self._setNumber(4, value)

    def getProgressPoints(self):
        return self._getArray(5)

    def setProgressPoints(self, value):
        self._setArray(5, value)

    @staticmethod
    def getProgressPointsType():
        return ProgressPointsModel

    def _initialize(self):
        super(WeeklyQuestsModel, self)._initialize()
        self._addStringProperty('seasonState')
        self._addNumberProperty('resetTimeLeft', 0)
        self._addArrayProperty('questCards', Array())
        self._addNumberProperty('currentTokenValue', 0)
        self._addNumberProperty('previousTokenValue', 0)
        self._addArrayProperty('progressPoints', Array())
        self.onAnimationStart = self._addCommand('onAnimationStart')
        self.onAnimationEnd = self._addCommand('onAnimationEnd')
