# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/statistic_reward_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class StatisticRewardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(StatisticRewardModel, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(0)

    def setRewards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def getRewardCount(self):
        return self._getNumber(1)

    def setRewardCount(self, value):
        self._setNumber(1, value)

    def getBonusGroup(self):
        return self._getString(2)

    def setBonusGroup(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(StatisticRewardModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
        self._addNumberProperty('rewardCount', 0)
        self._addStringProperty('bonusGroup', '')
