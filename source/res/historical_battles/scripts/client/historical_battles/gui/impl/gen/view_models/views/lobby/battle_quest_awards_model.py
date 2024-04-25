# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/battle_quest_awards_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class BattleStatus(Enum):
    INPROGRESS = 'inProgress'
    COMPLETED = 'completed'


class BattleQuestAwardsModel(ViewModel):
    __slots__ = ('onApprove', 'onClose', 'onHangarClick', 'onShopClick')

    def __init__(self, properties=5, commands=4):
        super(BattleQuestAwardsModel, self).__init__(properties=properties, commands=commands)

    def getBattleStatus(self):
        return BattleStatus(self._getString(0))

    def setBattleStatus(self, value):
        self._setString(0, value.value)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getHasMainVehicle(self):
        return self._getBool(2)

    def setHasMainVehicle(self, value):
        self._setBool(2, value)

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRewardsType():
        return RewardItemModel

    def getMainRewards(self):
        return self._getArray(4)

    def setMainRewards(self, value):
        self._setArray(4, value)

    @staticmethod
    def getMainRewardsType():
        return RewardItemModel

    def _initialize(self):
        super(BattleQuestAwardsModel, self)._initialize()
        self._addStringProperty('battleStatus')
        self._addNumberProperty('level', 0)
        self._addBoolProperty('hasMainVehicle', False)
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('mainRewards', Array())
        self.onApprove = self._addCommand('onApprove')
        self.onClose = self._addCommand('onClose')
        self.onHangarClick = self._addCommand('onHangarClick')
        self.onShopClick = self._addCommand('onShopClick')
