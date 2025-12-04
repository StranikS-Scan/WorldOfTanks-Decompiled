# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/surprise_machine/robot_tv_rewards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class RobotTvRewardsViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=2, commands=1):
        super(RobotTvRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getTokensUsed(self):
        return self._getNumber(0)

    def setTokensUsed(self, value):
        self._setNumber(0, value)

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def _initialize(self):
        super(RobotTvRewardsViewModel, self)._initialize()
        self._addNumberProperty('tokensUsed', 10)
        self._addArrayProperty('rewards', Array())
        self.onClose = self._addCommand('onClose')
