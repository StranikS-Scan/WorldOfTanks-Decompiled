# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/meta_view/claim_rewards_model.py
from frameworks.wulf import ViewModel

class ClaimRewardsModel(ViewModel):
    __slots__ = ('onGoToRewardSelection',)

    def __init__(self, properties=2, commands=1):
        super(ClaimRewardsModel, self).__init__(properties=properties, commands=commands)

    def getRewardsCount(self):
        return self._getNumber(0)

    def setRewardsCount(self, value):
        self._setNumber(0, value)

    def getIsDisabled(self):
        return self._getBool(1)

    def setIsDisabled(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(ClaimRewardsModel, self)._initialize()
        self._addNumberProperty('rewardsCount', 0)
        self._addBoolProperty('isDisabled', False)
        self.onGoToRewardSelection = self._addCommand('onGoToRewardSelection')
