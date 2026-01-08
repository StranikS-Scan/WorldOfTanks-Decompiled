# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/game_params_common/scope.py
from enum import IntEnum, unique

@unique
class GameParamsScopeFlags(IntEnum):
    BASE = 1
    CLIENT = 2
    CELL_ARENA = 4


class CellArenaScopeContext(object):
    __slots__ = ('bonusType', 'bonusCapsOverrides', 'gameplayID')

    def __init__(self, bonusType, bonusCapsOverrides, gameplayID):
        self.bonusType = bonusType
        self.bonusCapsOverrides = bonusCapsOverrides
        self.gameplayID = gameplayID


def clientFilter(params):
    return bool(params & GameParamsScopeFlags.CLIENT)


def cellArenaFilter(params):
    return bool(params & GameParamsScopeFlags.CELL_ARENA)
