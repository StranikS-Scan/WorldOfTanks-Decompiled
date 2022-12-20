# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/frontline_lvl_range_rewards.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_reward_model import FrontlineRewardModel

class FrontlineLvlRangeRewards(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(FrontlineLvlRangeRewards, self).__init__(properties=properties, commands=commands)

    def getLvlStart(self):
        return self._getNumber(0)

    def setLvlStart(self, value):
        self._setNumber(0, value)

    def getLvlEnd(self):
        return self._getNumber(1)

    def setLvlEnd(self, value):
        self._setNumber(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return FrontlineRewardModel

    def _initialize(self):
        super(FrontlineLvlRangeRewards, self)._initialize()
        self._addNumberProperty('lvlStart', 0)
        self._addNumberProperty('lvlEnd', 0)
        self._addArrayProperty('rewards', Array())
