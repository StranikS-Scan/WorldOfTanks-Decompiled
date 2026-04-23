# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/battle_control/arena_info/ls_squad_finder.py
from __future__ import absolute_import
from future.utils import lrange
from gui.battle_control.arena_info.squad_finder import TeamScopeNumberingFinder

class LSTeamScopeNumberingFinder(TeamScopeNumberingFinder):
    __slots__ = ()

    @classmethod
    def _getSquadRange(cls):
        return lrange(2, 6)
