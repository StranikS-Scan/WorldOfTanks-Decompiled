# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/battle_control/arena_info/arena_vos.py
from enum import Enum
from comp7_core.gui.battle_control.arena_info.arena_vos import Comp7CoreKeys
_DEFAULT_ROLE_SKILL_LEVEL = 0
_DEFAULT_PLAYER_RANK = 0
_DEFAULT_PLAYER_DIVISION = 0

class Comp7Keys(Enum):
    RANK = 'rank'
    IS_QUAL_ACTIVE = 'isQualActive'

    @staticmethod
    def getKeys(static=True):
        return [(Comp7CoreKeys.ROLE_SKILL_LEVEL, _DEFAULT_ROLE_SKILL_LEVEL),
         (Comp7Keys.RANK, (_DEFAULT_PLAYER_RANK, _DEFAULT_PLAYER_DIVISION)),
         (Comp7CoreKeys.VOIP_CONNECTED, False),
         (Comp7Keys.IS_QUAL_ACTIVE, False)] if static else []

    @staticmethod
    def getSortingKeys(static=True):
        return [Comp7Keys.RANK] if static else []


class TournamentComp7Keys(Enum):

    @staticmethod
    def getKeys(static=True):
        return [(Comp7CoreKeys.ROLE_SKILL_LEVEL, _DEFAULT_ROLE_SKILL_LEVEL), (Comp7CoreKeys.VOIP_CONNECTED, False)] if static else []

    @staticmethod
    def getSortingKeys(static=True):
        return []
