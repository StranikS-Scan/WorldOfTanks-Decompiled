# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/rewards_model.py
from frameworks.wulf import ViewModel

class RewardsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RewardsModel, self).__init__(properties=properties, commands=commands)

    def getRewardName(self):
        return self._getString(0)

    def setRewardName(self, value):
        self._setString(0, value)

    def getCount(self):
        return self._getNumber(1)

    def setCount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(RewardsModel, self)._initialize()
        self._addStringProperty('rewardName', '')
        self._addNumberProperty('count', 0)
