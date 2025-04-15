# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/battle_control/arena_info/hb_squad_finder.py
from gui.battle_control.arena_info.squad_finder import TeamScopeNumberingFinder

class HBTeamScopeNumberingFinder(TeamScopeNumberingFinder):
    __slots__ = ()

    @classmethod
    def _getSquadRange(cls):
        return xrange(2, 6)
