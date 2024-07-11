# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/lootboxes_rewards_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.key_type_model import KeyTypeModel

class LootboxesRewardsViewModel(ViewModel):
    __slots__ = ('onClose', 'showVehicleInHangar')
    ARG_REWARD_INDEX = 'tooltipId'
    MAX_MAIN_REWARDS = 3
    MAX_VISIBLE_REWARDS = 9

    def __init__(self, properties=7, commands=2):
        super(LootboxesRewardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def keyType(self):
        return self._getViewModel(0)

    @staticmethod
    def getKeyTypeType():
        return KeyTypeModel

    def getLootBoxName(self):
        return self._getResource(1)

    def setLootBoxName(self, value):
        self._setResource(1, value)

    def getLootBoxIconName(self):
        return self._getString(2)

    def setLootBoxIconName(self, value):
        self._setString(2, value)

    def getCountFailKey(self):
        return self._getNumber(3)

    def setCountFailKey(self, value):
        self._setNumber(3, value)

    def getLootBoxOpenCount(self):
        return self._getNumber(4)

    def setLootBoxOpenCount(self, value):
        self._setNumber(4, value)

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def getMainRewards(self):
        return self._getArray(6)

    def setMainRewards(self, value):
        self._setArray(6, value)

    @staticmethod
    def getMainRewardsType():
        return BonusModel

    def _initialize(self):
        super(LootboxesRewardsViewModel, self)._initialize()
        self._addViewModelProperty('keyType', KeyTypeModel())
        self._addResourceProperty('lootBoxName', R.invalid())
        self._addStringProperty('lootBoxIconName', '')
        self._addNumberProperty('countFailKey', 0)
        self._addNumberProperty('lootBoxOpenCount', 0)
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('mainRewards', Array())
        self.onClose = self._addCommand('onClose')
        self.showVehicleInHangar = self._addCommand('showVehicleInHangar')
