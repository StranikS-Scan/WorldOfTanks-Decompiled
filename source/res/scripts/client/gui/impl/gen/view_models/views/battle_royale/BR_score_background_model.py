# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/BR_score_background_model.py
from frameworks.wulf import ViewModel

class BRScoreBackgroundModel(ViewModel):
    __slots__ = ()

    def getCountChevrones(self):
        return self._getNumber(0)

    def setCountChevrones(self, value):
        self._setNumber(0, value)

    def getCount(self):
        return self._getNumber(1)

    def setCount(self, value):
        self._setNumber(1, value)

    def getIsWinner(self):
        return self._getBool(2)

    def setIsWinner(self, value):
        self._setBool(2, value)

    def getUserCurrent(self):
        return self._getBool(3)

    def setUserCurrent(self, value):
        self._setBool(3, value)

    def getIsInBattle(self):
        return self._getBool(4)

    def setIsInBattle(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(BRScoreBackgroundModel, self)._initialize()
        self._addNumberProperty('countChevrones', 0)
        self._addNumberProperty('count', 0)
        self._addBoolProperty('isWinner', False)
        self._addBoolProperty('userCurrent', False)
        self._addBoolProperty('isInBattle', False)
