# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/fun_random_rewards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class FunRandomRewardsViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=3, commands=1):
        super(FunRandomRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getAssetsPointer(self):
        return self._getString(0)

    def setAssetsPointer(self, value):
        self._setString(0, value)

    def getMainRewards(self):
        return self._getArray(1)

    def setMainRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getMainRewardsType():
        return ItemBonusModel

    def getAdditionalRewards(self):
        return self._getArray(2)

    def setAdditionalRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getAdditionalRewardsType():
        return ItemBonusModel

    def _initialize(self):
        super(FunRandomRewardsViewModel, self)._initialize()
        self._addStringProperty('assetsPointer', '')
        self._addArrayProperty('mainRewards', Array())
        self._addArrayProperty('additionalRewards', Array())
        self.onClose = self._addCommand('onClose')
