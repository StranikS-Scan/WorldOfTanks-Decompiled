# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/battle_control/arena_info/portal_squad_finder.py
from gui.battle_control.arena_info.squad_finder import TeamScopeNumberingFinder

class PortalTeamScopeNumberingFinder(TeamScopeNumberingFinder):
    __slots__ = ()

    @classmethod
    def _getSquadRange(cls):
        return xrange(2, 6)
