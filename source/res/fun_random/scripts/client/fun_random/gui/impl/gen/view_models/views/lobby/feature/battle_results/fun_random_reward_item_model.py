# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/battle_results/fun_random_reward_item_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.battle_results.reward_item_model import RewardItemModel

class FunRewardTypes(Enum):
    CREDITS = 'credits'
    GOLD = 'gold'
    CRYSTALS = 'crystal'
    XP = 'xp'
    FREE_XP = 'freeXP'
    TANKMEN_XP = 'tankmenXP'


class FunRandomRewardItemModel(RewardItemModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(FunRandomRewardItemModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(FunRandomRewardItemModel, self)._initialize()
