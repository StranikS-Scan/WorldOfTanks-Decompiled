# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/lobby/post_battle_results_view/fort_rush_reward_item_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.battle_results.reward_item_model import RewardItemModel

class FortRushRewardTypes(Enum):
    CREDITS = 'credits'
    XP = 'xp'
    PROGRESSION_POINTS = 'progressionPoints'


class FortRushRewardItemModel(RewardItemModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(FortRushRewardItemModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(FortRushRewardItemModel, self)._initialize()
