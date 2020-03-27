# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/items/tournament_items.py
from collections import namedtuple
from gui.prb_control.items.stronghold_items import StrongholdSettings

def isEnemyBattleIndex(index):
    return index >= 4


class TournamentSettings(StrongholdSettings):

    def isTournamentUnitFreezed(self):
        return super(TournamentSettings, self).isStrongholdUnitFreezed()


TournamentUnitStats = namedtuple('UnitStats', ('readyCount', 'occupiedSlotsCount', 'openedSlotsCount', 'freeSlotsCount', 'curTotalLevel', 'levelsSeq', 'clanMembersInRoster', 'legionariesInRoster', 'playersMatchingSlotsCount'))
TournamentUnitStats.__new__.__defaults__ = (0,
 0,
 0,
 0,
 0,
 (),
 0,
 0,
 0)
