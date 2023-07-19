# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/royale_models.py
from collections import namedtuple
from season_common import GameSeason

class BattleRoyaleCycle(namedtuple('BattleRoyaleCycle', 'ID, status, startDate, endDate, ordinalNumber, announceOnly')):

    def __cmp__(self, other):
        return cmp(self.ID, other.ID)

    def getUserName(self):
        return str(self.ordinalNumber)

    def getEpicCycleNumber(self):
        return self.ordinalNumber


class BattleRoyaleSeason(GameSeason):

    def _buildCycle(self, idx, status, start, end, number, announceOnly):
        return BattleRoyaleCycle(idx, status, start, end, number, announceOnly)
