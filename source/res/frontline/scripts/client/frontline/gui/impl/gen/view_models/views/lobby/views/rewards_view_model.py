# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/rewards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_lvl_range_rewards import FrontlineLvlRangeRewards

class RewardsViewModel(ViewModel):
    __slots__ = ('onClaimRewards',)

    def __init__(self, properties=5, commands=1):
        super(RewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getFrontlineState(self):
        return self._getString(0)

    def setFrontlineState(self, value):
        self._setString(0, value)

    def getSelectableRewardsCount(self):
        return self._getNumber(1)

    def setSelectableRewardsCount(self, value):
        self._setNumber(1, value)

    def getFrontlineLevel(self):
        return self._getNumber(2)

    def setFrontlineLevel(self, value):
        self._setNumber(2, value)

    def getIsBattlePassComplete(self):
        return self._getBool(3)

    def setIsBattlePassComplete(self, value):
        self._setBool(3, value)

    def getRewards(self):
        return self._getArray(4)

    def setRewards(self, value):
        self._setArray(4, value)

    @staticmethod
    def getRewardsType():
        return FrontlineLvlRangeRewards

    def _initialize(self):
        super(RewardsViewModel, self)._initialize()
        self._addStringProperty('frontlineState', '')
        self._addNumberProperty('selectableRewardsCount', 0)
        self._addNumberProperty('frontlineLevel', 0)
        self._addBoolProperty('isBattlePassComplete', False)
        self._addArrayProperty('rewards', Array())
        self.onClaimRewards = self._addCommand('onClaimRewards')
