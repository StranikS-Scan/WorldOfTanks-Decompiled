# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_quest_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.quest_simplification_model import QuestSimplificationModel

class NewYearQuestModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(NewYearQuestModel, self).__init__(properties=properties, commands=commands)

    @property
    def reward(self):
        return self._getViewModel(0)

    @property
    def simplification(self):
        return self._getViewModel(1)

    def getId(self):
        return self._getNumber(2)

    def setId(self, value):
        self._setNumber(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getIcon(self):
        return self._getString(4)

    def setIcon(self, value):
        self._setString(4, value)

    def getIsCumulative(self):
        return self._getBool(5)

    def setIsCumulative(self, value):
        self._setBool(5, value)

    def getCurrentProgress(self):
        return self._getNumber(6)

    def setCurrentProgress(self, value):
        self._setNumber(6, value)

    def getFinalProgress(self):
        return self._getNumber(7)

    def setFinalProgress(self, value):
        self._setNumber(7, value)

    def getGoalValue(self):
        return self._getNumber(8)

    def setGoalValue(self, value):
        self._setNumber(8, value)

    def getLevel(self):
        return self._getNumber(9)

    def setLevel(self, value):
        self._setNumber(9, value)

    def getIsCompleted(self):
        return self._getBool(10)

    def setIsCompleted(self, value):
        self._setBool(10, value)

    def getIsVisited(self):
        return self._getBool(11)

    def setIsVisited(self, value):
        self._setBool(11, value)

    def getIsCompletedAnimationShown(self):
        return self._getBool(12)

    def setIsCompletedAnimationShown(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(NewYearQuestModel, self)._initialize()
        self._addViewModelProperty('reward', UserListModel())
        self._addViewModelProperty('simplification', QuestSimplificationModel())
        self._addNumberProperty('id', 0)
        self._addStringProperty('description', '')
        self._addStringProperty('icon', '')
        self._addBoolProperty('isCumulative', False)
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('finalProgress', 0)
        self._addNumberProperty('goalValue', 0)
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isCompleted', False)
        self._addBoolProperty('isVisited', False)
        self._addBoolProperty('isCompletedAnimationShown', False)
