# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/birthday/progression.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.progression_level import ProgressionLevel

class Progression(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(Progression, self).__init__(properties=properties, commands=commands)

    def getCurrentLevel(self):
        return self._getNumber(0)

    def setCurrentLevel(self, value):
        self._setNumber(0, value)

    def getCurrentPoints(self):
        return self._getNumber(1)

    def setCurrentPoints(self, value):
        self._setNumber(1, value)

    def getPointsDeltaFrom(self):
        return self._getNumber(2)

    def setPointsDeltaFrom(self, value):
        self._setNumber(2, value)

    def getInfinityLevelCompleteCount(self):
        return self._getNumber(3)

    def setInfinityLevelCompleteCount(self, value):
        self._setNumber(3, value)

    def getInfinityStartPoints(self):
        return self._getNumber(4)

    def setInfinityStartPoints(self, value):
        self._setNumber(4, value)

    def getInfinityMaxPoints(self):
        return self._getNumber(5)

    def setInfinityMaxPoints(self, value):
        self._setNumber(5, value)

    def getInfinitySubstagesCount(self):
        return self._getNumber(6)

    def setInfinitySubstagesCount(self, value):
        self._setNumber(6, value)

    def getInfinityDeltaFrom(self):
        return self._getNumber(7)

    def setInfinityDeltaFrom(self, value):
        self._setNumber(7, value)

    def getLevels(self):
        return self._getArray(8)

    def setLevels(self, value):
        self._setArray(8, value)

    @staticmethod
    def getLevelsType():
        return ProgressionLevel

    def getInfinityRewards(self):
        return self._getArray(9)

    def setInfinityRewards(self, value):
        self._setArray(9, value)

    @staticmethod
    def getInfinityRewardsType():
        return TokenBonusModel

    def _initialize(self):
        super(Progression, self)._initialize()
        self._addNumberProperty('currentLevel', 1)
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('pointsDeltaFrom', 0)
        self._addNumberProperty('infinityLevelCompleteCount', 0)
        self._addNumberProperty('infinityStartPoints', 0)
        self._addNumberProperty('infinityMaxPoints', 0)
        self._addNumberProperty('infinitySubstagesCount', 0)
        self._addNumberProperty('infinityDeltaFrom', 0)
        self._addArrayProperty('levels', Array())
        self._addArrayProperty('infinityRewards', Array())
