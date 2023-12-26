# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/sack_reward_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.reward_item_model import RewardItemModel

class SackRewardModel(RewardItemModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(SackRewardModel, self).__init__(properties=properties, commands=commands)

    def getItemType(self):
        return self._getString(14)

    def setItemType(self, value):
        self._setString(14, value)

    def _initialize(self):
        super(SackRewardModel, self)._initialize()
        self._addStringProperty('itemType', 'style')
