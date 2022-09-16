# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/views/rewards_screen_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.comp7_bonus_model import Comp7BonusModel

class Type(IntEnum):
    RANK = 0
    DIVISION = 1
    FIRSTRANKREWARDS = 2
    RANKREWARDS = 3
    WINREWARDS = 4


class Rank(IntEnum):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5
    SIXTH = 6
    SEVENTH = 7


class Division(IntEnum):
    A = 0
    B = 1
    C = 2
    D = 3


class RewardsScreenModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=7, commands=1):
        super(RewardsScreenModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return Type(self._getNumber(0))

    def setType(self, value):
        self._setNumber(0, value.value)

    def getRank(self):
        return Rank(self._getNumber(1))

    def setRank(self, value):
        self._setNumber(1, value.value)

    def getHasRankInactivity(self):
        return self._getBool(2)

    def setHasRankInactivity(self, value):
        self._setBool(2, value)

    def getDivision(self):
        return Division(self._getNumber(3))

    def setDivision(self, value):
        self._setNumber(3, value.value)

    def getWinCount(self):
        return self._getNumber(4)

    def setWinCount(self, value):
        self._setNumber(4, value)

    def getMainRewards(self):
        return self._getArray(5)

    def setMainRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getMainRewardsType():
        return Comp7BonusModel

    def getAdditionalRewards(self):
        return self._getArray(6)

    def setAdditionalRewards(self, value):
        self._setArray(6, value)

    @staticmethod
    def getAdditionalRewardsType():
        return Comp7BonusModel

    def _initialize(self):
        super(RewardsScreenModel, self)._initialize()
        self._addNumberProperty('type')
        self._addNumberProperty('rank')
        self._addBoolProperty('hasRankInactivity', False)
        self._addNumberProperty('division')
        self._addNumberProperty('winCount', 0)
        self._addArrayProperty('mainRewards', Array())
        self._addArrayProperty('additionalRewards', Array())
        self.onClose = self._addCommand('onClose')
