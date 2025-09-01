# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/battle_control/arena_info/squad_finder.py
from gui.battle_control.arena_info.squad_finder import TeamScopeNumberingFinder

class Comp7LightTeamScopeNumberingFinder(TeamScopeNumberingFinder):
    __slots__ = ()

    @classmethod
    def _getSquadRange(cls):
        return xrange(2, 8)
