# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/lootboxes/reward_kit_guaranteed_reward_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class RewardState(IntEnum):
    NORMAL = 0
    DISABLED = 1


class RewardKitGuaranteedRewardModel(ViewModel):
    __slots__ = ('onShowInfo',)

    def __init__(self, properties=5, commands=1):
        super(RewardKitGuaranteedRewardModel, self).__init__(properties=properties, commands=commands)

    def getRealm(self):
        return self._getString(0)

    def setRealm(self, value):
        self._setString(0, value)

    def getMaxBoxesCount(self):
        return self._getNumber(1)

    def setMaxBoxesCount(self, value):
        self._setNumber(1, value)

    def getIsPremiumType(self):
        return self._getBool(2)

    def setIsPremiumType(self, value):
        self._setBool(2, value)

    def getIsFocused(self):
        return self._getBool(3)

    def setIsFocused(self, value):
        self._setBool(3, value)

    def getState(self):
        return RewardState(self._getNumber(4))

    def setState(self, value):
        self._setNumber(4, value.value)

    def _initialize(self):
        super(RewardKitGuaranteedRewardModel, self)._initialize()
        self._addStringProperty('realm', '')
        self._addNumberProperty('maxBoxesCount', 0)
        self._addBoolProperty('isPremiumType', False)
        self._addBoolProperty('isFocused', False)
        self._addNumberProperty('state')
        self.onShowInfo = self._addCommand('onShowInfo')
