# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/feature/battle_results/white_tiger_reward_item_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.battle_results.reward_item_model import RewardItemModel

class WhiteTigerRewardTypes(Enum):
    CREDITS = 'credits'
    GOLD = 'gold'
    CRYSTALS = 'crystal'
    XP = 'xp'
    FREE_XP = 'freeXP'
    TANKMEN_XP = 'tankmenXP'
    ACHIEVEMENT = 'achievement'
    EQUIP_COIN = 'equipCoin'
    PROGRESSION_STAMPS = 'stamp'
    WT_TICKET = 'wtevent_Ticket'
    BATTLE_PASS_POINTS = 'battlepassPoints'
    LOOT_BOX = 'wtevent_lootBox'
    CUSTOMIZATIONS = 'customizations'


class WhiteTigerRewardItemModel(RewardItemModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(WhiteTigerRewardItemModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(WhiteTigerRewardItemModel, self)._initialize()
