# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/battle_control/arena_info/squad_finder.py
from gui.battle_control.arena_info.squad_finder import TeamScopeNumberingFinder

class Comp7TeamScopeNumberingFinder(TeamScopeNumberingFinder):
    __slots__ = ()

    @classmethod
    def _getSquadRange(cls):
        return xrange(2, 8)
