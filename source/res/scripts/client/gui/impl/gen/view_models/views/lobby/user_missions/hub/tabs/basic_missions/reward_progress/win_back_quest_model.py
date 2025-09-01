# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/hub/tabs/basic_missions/reward_progress/win_back_quest_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class WinBackQuestModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(WinBackQuestModel, self).__init__(properties=properties, commands=commands)

    def getQuestNumber(self):
        return self._getNumber(0)

    def setQuestNumber(self, value):
        self._setNumber(0, value)

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def _initialize(self):
        super(WinBackQuestModel, self)._initialize()
        self._addNumberProperty('questNumber', 0)
        self._addArrayProperty('rewards', Array())
