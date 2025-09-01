# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/random/random_reward_item_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.battle_results.reward_item_model import RewardItemModel

class RandomRewardTypes(Enum):
    CREDITS = 'credits'
    GOLD = 'gold'
    CRYSTALS = 'crystal'
    XP = 'xp'


class RandomRewardItemModel(RewardItemModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RandomRewardItemModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(RandomRewardItemModel, self)._initialize()
