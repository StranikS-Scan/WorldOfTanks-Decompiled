# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/battle_quest_awards_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class BattleStatus(Enum):
    INPROGRESS = 'inProgress'
    COMPLETED = 'completed'


class AwardsViewType(Enum):
    PROGRESSION = 'progression'
    QUESTS = 'quests'


class BattleQuestAwardsModel(ViewModel):
    __slots__ = ('onApprove', 'onClose', 'onHangarClick', 'onShopClick')

    def __init__(self, properties=10, commands=4):
        super(BattleQuestAwardsModel, self).__init__(properties=properties, commands=commands)

    def getFrontName(self):
        return self._getString(0)

    def setFrontName(self, value):
        self._setString(0, value)

    def getBattleStatus(self):
        return BattleStatus(self._getString(1))

    def setBattleStatus(self, value):
        self._setString(1, value.value)

    def getAwardsViewType(self):
        return AwardsViewType(self._getString(2))

    def setAwardsViewType(self, value):
        self._setString(2, value.value)

    def getLevel(self):
        return self._getNumber(3)

    def setLevel(self, value):
        self._setNumber(3, value)

    def getHasVehicleInRewards(self):
        return self._getBool(4)

    def setHasVehicleInRewards(self, value):
        self._setBool(4, value)

    def getHasVehicleInInventory(self):
        return self._getBool(5)

    def setHasVehicleInInventory(self, value):
        self._setBool(5, value)

    def getFinishStage(self):
        return self._getBool(6)

    def setFinishStage(self, value):
        self._setBool(6, value)

    def getIsSpecial(self):
        return self._getBool(7)

    def setIsSpecial(self, value):
        self._setBool(7, value)

    def getRewards(self):
        return self._getArray(8)

    def setRewards(self, value):
        self._setArray(8, value)

    @staticmethod
    def getRewardsType():
        return RewardItemModel

    def getMainRewards(self):
        return self._getArray(9)

    def setMainRewards(self, value):
        self._setArray(9, value)

    @staticmethod
    def getMainRewardsType():
        return RewardItemModel

    def _initialize(self):
        super(BattleQuestAwardsModel, self)._initialize()
        self._addStringProperty('frontName', '')
        self._addStringProperty('battleStatus')
        self._addStringProperty('awardsViewType')
        self._addNumberProperty('level', 0)
        self._addBoolProperty('hasVehicleInRewards', False)
        self._addBoolProperty('hasVehicleInInventory', False)
        self._addBoolProperty('finishStage', False)
        self._addBoolProperty('isSpecial', False)
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('mainRewards', Array())
        self.onApprove = self._addCommand('onApprove')
        self.onClose = self._addCommand('onClose')
        self.onHangarClick = self._addCommand('onHangarClick')
        self.onShopClick = self._addCommand('onShopClick')
