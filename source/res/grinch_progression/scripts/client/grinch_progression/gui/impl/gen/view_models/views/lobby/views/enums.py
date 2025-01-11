# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/gen/view_models/views/lobby/views/enums.py
from enum import Enum

class VehicleRole(Enum):
    CARRIER = 'carrier'
    SUPPORT = 'support'
    ASSAULT = 'assault'


class RewardRarity(Enum):
    COMMON = 'common'
    UNCOMMON = 'uncommon'
    RARE = 'rare'
    EPIC = 'epic'


class RewardState(Enum):
    NOTAVAILABLE = 'notAvailable'
    AVAILABLE = 'available'
    CLAIMED = 'claimed'


class HintState(Enum):
    NONE = 'none'
    VEHICLE = 'vehicle'
    COINS = 'coins'
    BATTLE = 'battle'
    MOVE = 'move'
    MISSIONS = 'missions'
    FINISH = 'finish'
