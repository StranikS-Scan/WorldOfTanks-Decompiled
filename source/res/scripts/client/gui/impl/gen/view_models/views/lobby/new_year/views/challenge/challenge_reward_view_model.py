# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/challenge_reward_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class ChallengeRewardViewModel(ViewModel):
    __slots__ = ('sendCloseEvent', 'goToNyVehicleBranch')
    LOW_GRAPHICS_PRESET = 4

    def __init__(self, properties=6, commands=2):
        super(ChallengeRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getCompletedQuests(self):
        return self._getNumber(0)

    def setCompletedQuests(self, value):
        self._setNumber(0, value)

    def getIsFinal(self):
        return self._getBool(1)

    def setIsFinal(self, value):
        self._setBool(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    def getIsDiscountPopoverOpened(self):
        return self._getBool(3)

    def setIsDiscountPopoverOpened(self, value):
        self._setBool(3, value)

    def getSyncInitiator(self):
        return self._getNumber(4)

    def setSyncInitiator(self, value):
        self._setNumber(4, value)

    def getRecommendedGraphicsPreset(self):
        return self._getNumber(5)

    def setRecommendedGraphicsPreset(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(ChallengeRewardViewModel, self)._initialize()
        self._addNumberProperty('completedQuests', 0)
        self._addBoolProperty('isFinal', False)
        self._addArrayProperty('rewards', Array())
        self._addBoolProperty('isDiscountPopoverOpened', False)
        self._addNumberProperty('syncInitiator', 0)
        self._addNumberProperty('recommendedGraphicsPreset', 0)
        self.sendCloseEvent = self._addCommand('sendCloseEvent')
        self.goToNyVehicleBranch = self._addCommand('goToNyVehicleBranch')
