# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/ny_challenge_completed_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.progress_reward_item_model import ProgressRewardItemModel

class NyChallengeCompletedModel(ViewModel):
    __slots__ = ('onStylePreview',)

    def __init__(self, properties=3, commands=1):
        super(NyChallengeCompletedModel, self).__init__(properties=properties, commands=commands)

    def getDiscountPopoverId(self):
        return self._getString(0)

    def setDiscountPopoverId(self, value):
        self._setString(0, value)

    def getDiscountRewards(self):
        return self._getArray(1)

    def setDiscountRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getDiscountRewardsType():
        return ProgressRewardItemModel

    def getRemainingRewards(self):
        return self._getArray(2)

    def setRemainingRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRemainingRewardsType():
        return ProgressRewardItemModel

    def _initialize(self):
        super(NyChallengeCompletedModel, self)._initialize()
        self._addStringProperty('discountPopoverId', '')
        self._addArrayProperty('discountRewards', Array())
        self._addArrayProperty('remainingRewards', Array())
        self.onStylePreview = self._addCommand('onStylePreview')
