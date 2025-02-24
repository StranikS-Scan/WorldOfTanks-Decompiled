# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/enums.py
from enum import Enum, IntEnum

class MetaRootViews(IntEnum):
    PROGRESSION = 0
    RANKREWARDS = 1
    YEARLYREWARDS = 2
    WEEKLYQUESTS = 3
    SHOP = 4
    LEADERBOARD = 5
    YEARLYSTATISTICS = 6


class Rank(IntEnum):
    FIRST = 6
    SECOND = 5
    THIRD = 4
    FOURTH = 3
    FIFTH = 2
    SIXTH = 1


class SeasonName(Enum):
    FIRST = 'first'
    SECOND = 'second'
    THIRD = 'third'


class Division(IntEnum):
    A = 1
    B = 2
    C = 3
    D = 4
    E = 5


class SeasonPointState(Enum):
    ACHIEVED = 'achieved'
    POSSIBLE = 'possible'
    NOTACHIEVED = 'notAchieved'
