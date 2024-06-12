# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/early_access/early_access_rewards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class EarlyAccessRewardsViewModel(ViewModel):
    __slots__ = ('onClose', 'onShowVehicle')
    ARG_REWARD_INDEX = 'tooltipId'
    MAX_REWARDS = 10

    def __init__(self, properties=3, commands=2):
        super(EarlyAccessRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getHasAllRewards(self):
        return self._getBool(0)

    def setHasAllRewards(self, value):
        self._setBool(0, value)

    def getMainRewards(self):
        return self._getArray(1)

    def setMainRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getMainRewardsType():
        return ItemBonusModel

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def _initialize(self):
        super(EarlyAccessRewardsViewModel, self)._initialize()
        self._addBoolProperty('hasAllRewards', False)
        self._addArrayProperty('mainRewards', Array())
        self._addArrayProperty('rewards', Array())
        self.onClose = self._addCommand('onClose')
        self.onShowVehicle = self._addCommand('onShowVehicle')
