# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/lootboxes_rewards_view_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.key_type_model import KeyTypeModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootbox_key_view_model import LootboxKeyViewModel

class Glows(Enum):
    DEFAULT = 'DEFAULT'
    UNIQUE = 'UNIQUE'


class LootboxesRewardsViewModel(ViewModel):
    __slots__ = ('onClose', 'showVehicleInHangar', 'onRepeatOpen')
    ARG_REWARD_INDEX = 'tooltipId'
    MAX_MAIN_REWARDS = 3
    MAX_VISIBLE_REWARDS = 9

    def __init__(self, properties=17, commands=3):
        super(LootboxesRewardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def lootboxKey(self):
        return self._getViewModel(0)

    @staticmethod
    def getLootboxKeyType():
        return LootboxKeyViewModel

    @property
    def keyType(self):
        return self._getViewModel(1)

    @staticmethod
    def getKeyTypeType():
        return KeyTypeModel

    def getIsHiddenCount(self):
        return self._getBool(2)

    def setIsHiddenCount(self, value):
        self._setBool(2, value)

    def getLootboxID(self):
        return self._getNumber(3)

    def setLootboxID(self, value):
        self._setNumber(3, value)

    def getLootBoxName(self):
        return self._getResource(4)

    def setLootBoxName(self, value):
        self._setResource(4, value)

    def getLootBoxIconName(self):
        return self._getString(5)

    def setLootBoxIconName(self, value):
        self._setString(5, value)

    def getLootBoxCount(self):
        return self._getNumber(6)

    def setLootBoxCount(self, value):
        self._setNumber(6, value)

    def getLootBoxOpenCount(self):
        return self._getNumber(7)

    def setLootBoxOpenCount(self, value):
        self._setNumber(7, value)

    def getSenderName(self):
        return self._getString(8)

    def setSenderName(self, value):
        self._setString(8, value)

    def getMoreSendersCount(self):
        return self._getNumber(9)

    def setMoreSendersCount(self, value):
        self._setNumber(9, value)

    def getPhraseRes(self):
        return self._getResource(10)

    def setPhraseRes(self, value):
        self._setResource(10, value)

    def getIsNameLoading(self):
        return self._getBool(11)

    def setIsNameLoading(self, value):
        self._setBool(11, value)

    def getLootBoxMaxOpenCount(self):
        return self._getNumber(12)

    def setLootBoxMaxOpenCount(self, value):
        self._setNumber(12, value)

    def getCountFailKey(self):
        return self._getNumber(13)

    def setCountFailKey(self, value):
        self._setNumber(13, value)

    def getGlowType(self):
        return Glows(self._getString(14))

    def setGlowType(self, value):
        self._setString(14, value.value)

    def getRewards(self):
        return self._getArray(15)

    def setRewards(self, value):
        self._setArray(15, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def getMainRewards(self):
        return self._getArray(16)

    def setMainRewards(self, value):
        self._setArray(16, value)

    @staticmethod
    def getMainRewardsType():
        return BonusModel

    def _initialize(self):
        super(LootboxesRewardsViewModel, self)._initialize()
        self._addViewModelProperty('lootboxKey', LootboxKeyViewModel())
        self._addViewModelProperty('keyType', KeyTypeModel())
        self._addBoolProperty('isHiddenCount', False)
        self._addNumberProperty('lootboxID', 0)
        self._addResourceProperty('lootBoxName', R.invalid())
        self._addStringProperty('lootBoxIconName', '')
        self._addNumberProperty('lootBoxCount', 0)
        self._addNumberProperty('lootBoxOpenCount', 0)
        self._addStringProperty('senderName', '')
        self._addNumberProperty('moreSendersCount', 0)
        self._addResourceProperty('phraseRes', R.invalid())
        self._addBoolProperty('isNameLoading', False)
        self._addNumberProperty('lootBoxMaxOpenCount', 0)
        self._addNumberProperty('countFailKey', 0)
        self._addStringProperty('glowType', Glows.DEFAULT.value)
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('mainRewards', Array())
        self.onClose = self._addCommand('onClose')
        self.showVehicleInHangar = self._addCommand('showVehicleInHangar')
        self.onRepeatOpen = self._addCommand('onRepeatOpen')
