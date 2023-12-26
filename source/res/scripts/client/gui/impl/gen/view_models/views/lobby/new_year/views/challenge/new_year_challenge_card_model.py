# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_challenge_card_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.challenge_reward_item_model import ChallengeRewardItemModel

class CardState(IntEnum):
    ACTIVE = 0
    COMPLETED = 1
    JUSTCOMPLETED = 2
    INTRANSITION = 3


class NewYearChallengeCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(NewYearChallengeCardModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getString(0)

    def setDescription(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getIsCumulative(self):
        return self._getBool(2)

    def setIsCumulative(self, value):
        self._setBool(2, value)

    def getCurrentProgress(self):
        return self._getNumber(3)

    def setCurrentProgress(self, value):
        self._setNumber(3, value)

    def getFinalProgress(self):
        return self._getNumber(4)

    def setFinalProgress(self, value):
        self._setNumber(4, value)

    def getGoalValue(self):
        return self._getNumber(5)

    def setGoalValue(self, value):
        self._setNumber(5, value)

    def getState(self):
        return CardState(self._getNumber(6))

    def setState(self, value):
        self._setNumber(6, value.value)

    def getIsVisited(self):
        return self._getBool(7)

    def setIsVisited(self, value):
        self._setBool(7, value)

    def getToken(self):
        return self._getString(8)

    def setToken(self, value):
        self._setString(8, value)

    def getRewards(self):
        return self._getArray(9)

    def setRewards(self, value):
        self._setArray(9, value)

    @staticmethod
    def getRewardsType():
        return ChallengeRewardItemModel

    def _initialize(self):
        super(NewYearChallengeCardModel, self)._initialize()
        self._addStringProperty('description', '')
        self._addStringProperty('icon', '')
        self._addBoolProperty('isCumulative', False)
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('finalProgress', 0)
        self._addNumberProperty('goalValue', 0)
        self._addNumberProperty('state')
        self._addBoolProperty('isVisited', False)
        self._addStringProperty('token', '')
        self._addArrayProperty('rewards', Array())
