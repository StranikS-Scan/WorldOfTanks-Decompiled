# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/feature_types.py
from collections import namedtuple
BattlePlayerData = namedtuple('_BattlePlayerData', ('name', 'clanAbbrev', 'spaID', 'arenaUniqueID'))

class ArenaData(object):
    __slots__ = ('arenaUniqueID', 'isLost', 'players')

    def __init__(self, arenaUniqueID, isLost, players):
        self.arenaUniqueID = arenaUniqueID
        self.isLost = isLost
        self.players = players

    def __repr__(self):
        return '{}({},{},{})'.format(self.__class__.__name__, self.arenaUniqueID, self.isLost, self.players)
