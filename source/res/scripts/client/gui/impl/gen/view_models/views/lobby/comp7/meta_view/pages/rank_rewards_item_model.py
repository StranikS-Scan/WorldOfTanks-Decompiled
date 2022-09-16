# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/pages/rank_rewards_item_model.py
from enum import IntEnum
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.comp7.comp7_bonus_model import Comp7BonusModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.progression_item_base_model import ProgressionItemBaseModel

class RankRewardsState(IntEnum):
    NOTACHIEVED = 0
    ACHIEVED = 1


class RankRewardsItemModel(ProgressionItemBaseModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(RankRewardsItemModel, self).__init__(properties=properties, commands=commands)

    def getRewardsState(self):
        return RankRewardsState(self._getNumber(4))

    def setRewardsState(self, value):
        self._setNumber(4, value.value)

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRewardsType():
        return Comp7BonusModel

    def getMainReward(self):
        return self._getArray(6)

    def setMainReward(self, value):
        self._setArray(6, value)

    @staticmethod
    def getMainRewardType():
        return Comp7BonusModel

    def _initialize(self):
        super(RankRewardsItemModel, self)._initialize()
        self._addNumberProperty('rewardsState')
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('mainReward', Array())
