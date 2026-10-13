# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/battle_control/arena_info/halloween_squad_finder.py
from __future__ import absolute_import
from builtins import range
from gui.battle_control.arena_info.squad_finder import TeamScopeNumberingFinder

class HalloweenTeamScopeNumberingFinder(TeamScopeNumberingFinder):
    __slots__ = ()

    @classmethod
    def _getSquadRange(cls):
        return range(2, 6)
