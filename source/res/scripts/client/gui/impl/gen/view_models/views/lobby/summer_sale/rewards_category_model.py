# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/summer_sale/rewards_category_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class RewardsCategoryModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RewardsCategoryModel, self).__init__(properties=properties, commands=commands)

    def getProbability(self):
        return self._getNumber(0)

    def setProbability(self, value):
        self._setNumber(0, value)

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def _initialize(self):
        super(RewardsCategoryModel, self)._initialize()
        self._addNumberProperty('probability', 0)
        self._addArrayProperty('rewards', Array())
