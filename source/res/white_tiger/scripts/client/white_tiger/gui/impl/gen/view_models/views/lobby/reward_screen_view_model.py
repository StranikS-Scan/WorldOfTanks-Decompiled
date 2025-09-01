# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/reward_screen_view_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class RewardScreenViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=4, commands=1):
        super(RewardScreenViewModel, self).__init__(properties=properties, commands=commands)

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

    def getHasCompleted(self):
        return self._getBool(3)

    def setHasCompleted(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(RewardScreenViewModel, self)._initialize()
        self._addStringProperty('assetsPointer', '')
        self._addArrayProperty('mainRewards', Array())
        self._addArrayProperty('additionalRewards', Array())
        self._addBoolProperty('hasCompleted', False)
        self.onClose = self._addCommand('onClose')
