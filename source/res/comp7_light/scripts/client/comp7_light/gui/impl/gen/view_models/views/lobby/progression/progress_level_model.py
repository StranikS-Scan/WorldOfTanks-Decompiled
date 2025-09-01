# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/gen/view_models/views/lobby/progression/progress_level_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class ProgressLevelModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(ProgressLevelModel, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(0)

    def setRewards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def _initialize(self):
        super(ProgressLevelModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
