# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/lootboxes_rewards_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class LootboxesRewardsViewModel(ViewModel):
    __slots__ = ('onClose', 'showVehicleInHangar')
    ARG_REWARD_INDEX = 'tooltipId'
    MAX_MAIN_REWARDS = 3
    MAX_VISIBLE_REWARDS = 9

    def __init__(self, properties=4, commands=2):
        super(LootboxesRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getLootBoxName(self):
        return self._getResource(0)

    def setLootBoxName(self, value):
        self._setResource(0, value)

    def getLootBoxIconName(self):
        return self._getString(1)

    def setLootBoxIconName(self, value):
        self._setString(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def getMainRewards(self):
        return self._getArray(3)

    def setMainRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getMainRewardsType():
        return BonusModel

    def _initialize(self):
        super(LootboxesRewardsViewModel, self)._initialize()
        self._addResourceProperty('lootBoxName', R.invalid())
        self._addStringProperty('lootBoxIconName', '')
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('mainRewards', Array())
        self.onClose = self._addCommand('onClose')
        self.showVehicleInHangar = self._addCommand('showVehicleInHangar')
