# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/common/fun_random_progression_stage.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class FunRandomProgressionStage(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(FunRandomProgressionStage, self).__init__(properties=properties, commands=commands)

    def getCurrentPoints(self):
        return self._getNumber(0)

    def setCurrentPoints(self, value):
        self._setNumber(0, value)

    def getMaximumPoints(self):
        return self._getNumber(1)

    def setMaximumPoints(self, value):
        self._setNumber(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def _initialize(self):
        super(FunRandomProgressionStage, self)._initialize()
        self._addNumberProperty('currentPoints', -1)
        self._addNumberProperty('maximumPoints', -1)
        self._addArrayProperty('rewards', Array())
