# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/royale_models.py
from __future__ import absolute_import
from collections import namedtuple
from past.builtins import cmp
from season_common import GameSeason

class BattleRoyaleCycle(namedtuple('BattleRoyaleCycle', 'ID, status, startDate, endDate, ordinalNumber, announceOnly')):

    def __eq__(self, other):
        return self.__compare(other) == 0

    def __ne__(self, other):
        return self.__compare(other) != 0

    def __lt__(self, other):
        return self.__compare(other) < 0

    def __le__(self, other):
        return self.__compare(other) <= 0

    def __gt__(self, other):
        return self.__compare(other) > 0

    def __ge__(self, other):
        return self.__compare(other) >= 0

    def __hash__(self):
        return self.ID

    def getUserName(self):
        return str(self.ordinalNumber)

    def getEpicCycleNumber(self):
        return self.ordinalNumber

    def __compare(self, other):
        return cmp(self.ID, other.ID)


class BattleRoyaleSeason(GameSeason):

    def _buildCycle(self, idx, status, start, end, number, announceOnly):
        return BattleRoyaleCycle(idx, status, start, end, number, announceOnly)
