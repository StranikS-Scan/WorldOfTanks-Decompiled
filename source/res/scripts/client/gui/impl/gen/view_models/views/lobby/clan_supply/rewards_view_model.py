# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/clan_supply/rewards_view_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class RewardingType(IntEnum):
    COMMON = 0
    ELITE = 1
    ELITE_WITH_VEHICLE = 2


class RewardsViewModel(ViewModel):
    __slots__ = ('onClose', 'onGoToHangar')

    def __init__(self, properties=3, commands=2):
        super(RewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return RewardingType(self._getNumber(0))

    def setType(self, value):
        self._setNumber(0, value.value)

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def getAdditionalRewards(self):
        return self._getArray(2)

    def setAdditionalRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getAdditionalRewardsType():
        return ItemBonusModel

    def _initialize(self):
        super(RewardsViewModel, self)._initialize()
        self._addNumberProperty('type')
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('additionalRewards', Array())
        self.onClose = self._addCommand('onClose')
        self.onGoToHangar = self._addCommand('onGoToHangar')
