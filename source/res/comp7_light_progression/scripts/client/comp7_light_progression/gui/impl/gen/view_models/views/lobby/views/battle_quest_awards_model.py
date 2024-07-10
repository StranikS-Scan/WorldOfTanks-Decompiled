# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light_progression/scripts/client/comp7_light_progression/gui/impl/gen/view_models/views/lobby/views/battle_quest_awards_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class BattleStatus(Enum):
    INPROGRESS = 'inProgress'
    COMPLETED = 'completed'


class BattleQuestAwardsModel(ViewModel):
    __slots__ = ('onApprove', 'onClose')

    def __init__(self, properties=3, commands=2):
        super(BattleQuestAwardsModel, self).__init__(properties=properties, commands=commands)

    def getBattleStatus(self):
        return BattleStatus(self._getString(0))

    def setBattleStatus(self, value):
        self._setString(0, value.value)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return RewardItemModel

    def _initialize(self):
        super(BattleQuestAwardsModel, self)._initialize()
        self._addStringProperty('battleStatus')
        self._addNumberProperty('level', 0)
        self._addArrayProperty('rewards', Array())
        self.onApprove = self._addCommand('onApprove')
        self.onClose = self._addCommand('onClose')
