# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/widget/base_battle_pass_model.py
from frameworks.wulf import ViewModel

class BaseBattlePassModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BaseBattlePassModel, self).__init__(properties=properties, commands=commands)

    def getRewardsHash(self):
        return self._getNumber(0)

    def setRewardsHash(self, value):
        self._setNumber(0, value)

    def getPointsEarned(self):
        return self._getNumber(1)

    def setPointsEarned(self, value):
        self._setNumber(1, value)

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(BaseBattlePassModel, self)._initialize()
        self._addNumberProperty('rewardsHash', 0)
        self._addNumberProperty('pointsEarned', 0)
        self._addNumberProperty('level', 0)
