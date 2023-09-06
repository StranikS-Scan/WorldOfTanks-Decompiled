# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/pages/rank_rewards_item_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.comp7.comp7_bonus_model import Comp7BonusModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.progression_item_base_model import ProgressionItemBaseModel

class RankRewardsItemModel(ProgressionItemBaseModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(RankRewardsItemModel, self).__init__(properties=properties, commands=commands)

    def getHasRewardsReceived(self):
        return self._getBool(4)

    def setHasRewardsReceived(self, value):
        self._setBool(4, value)

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRewardsType():
        return Comp7BonusModel

    def _initialize(self):
        super(RankRewardsItemModel, self)._initialize()
        self._addBoolProperty('hasRewardsReceived', False)
        self._addArrayProperty('rewards', Array())
