# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/progression_reward_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class ProgressionRewardViewModel(ViewModel):
    __slots__ = ('onClose', 'onSetBlur')

    def __init__(self, properties=4, commands=2):
        super(ProgressionRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getOpenedSlotsCount(self):
        return self._getNumber(0)

    def setOpenedSlotsCount(self, value):
        self._setNumber(0, value)

    def getIsFirstStage(self):
        return self._getBool(1)

    def setIsFirstStage(self, value):
        self._setBool(1, value)

    def getMainRewards(self):
        return self._getArray(2)

    def setMainRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getMainRewardsType():
        return BonusModel

    def getAdditionalRewards(self):
        return self._getArray(3)

    def setAdditionalRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getAdditionalRewardsType():
        return BonusModel

    def _initialize(self):
        super(ProgressionRewardViewModel, self)._initialize()
        self._addNumberProperty('openedSlotsCount', 0)
        self._addBoolProperty('isFirstStage', False)
        self._addArrayProperty('mainRewards', Array())
        self._addArrayProperty('additionalRewards', Array())
        self.onClose = self._addCommand('onClose')
        self.onSetBlur = self._addCommand('onSetBlur')
