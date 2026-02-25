# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/battle_quest_awards_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_royale_event_model import BattleRoyaleEventModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class BattleStatus(Enum):
    INPROGRESS = 'inProgress'
    COMPLETED = 'completed'


class BattleQuestAwardsModel(ViewModel):
    __slots__ = ('onApprove', 'onClose')

    def __init__(self, properties=4, commands=2):
        super(BattleQuestAwardsModel, self).__init__(properties=properties, commands=commands)

    @property
    def eventInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getEventInfoType():
        return BattleRoyaleEventModel

    def getBattleStatus(self):
        return BattleStatus(self._getString(1))

    def setBattleStatus(self, value):
        self._setString(1, value.value)

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRewardsType():
        return RewardItemModel

    def _initialize(self):
        super(BattleQuestAwardsModel, self)._initialize()
        self._addViewModelProperty('eventInfo', BattleRoyaleEventModel())
        self._addStringProperty('battleStatus')
        self._addNumberProperty('level', 0)
        self._addArrayProperty('rewards', Array())
        self.onApprove = self._addCommand('onApprove')
        self.onClose = self._addCommand('onClose')
