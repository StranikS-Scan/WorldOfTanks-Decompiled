# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/gen/view_models/views/lobby/views/progress_level_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class ProgressLevelModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ProgressLevelModel, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(0)

    def setRewards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def getIsSelectableReward(self):
        return self._getBool(1)

    def setIsSelectableReward(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(ProgressLevelModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
        self._addBoolProperty('isSelectableReward', False)
