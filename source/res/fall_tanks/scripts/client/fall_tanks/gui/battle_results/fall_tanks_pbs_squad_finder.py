# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_results/fall_tanks_pbs_squad_finder.py
from collections import defaultdict
from gui.battle_control.arena_info.squad_finder import ISquadFinder
from gui.battle_control.arena_info.settings import SQUAD_RANGE_TO_SHOW

class FallTanksPostbattleSquadFinder(ISquadFinder):
    __slots__ = ('__squadIndices', '__prbStats')

    def __init__(self, _):
        super(FallTanksPostbattleSquadFinder, self).__init__()
        self.__prbStats = defaultdict(set)
        self.__squadIndices = {}

    def clear(self):
        self.__squadIndices.clear()
        self.__prbStats.clear()

    def addVehicleInfo(self, team, prebattleID, vehicleID):
        if not prebattleID:
            return
        self.__prbStats[prebattleID].add(vehicleID)

    def getNumberOfSquads(self):
        return max(self.__squadIndices.values()) if self.__squadIndices else 0

    def getNumberOfSquadmen(self, team, prebattleID):
        pass

    def findSquads(self):
        squadRange = self._getSquadRange()
        for prebattleID, vehiclesIDs in self.__prbStats.items():
            if not vehiclesIDs or len(vehiclesIDs) not in squadRange:
                continue
            if prebattleID not in self.__squadIndices:
                if self.__squadIndices:
                    self.__squadIndices[prebattleID] = max(self.__squadIndices.values()) + 1
                else:
                    self.__squadIndices[prebattleID] = 1
            for vehicleID in vehiclesIDs:
                yield (vehicleID, self.__squadIndices[prebattleID])

    @classmethod
    def _getSquadRange(cls):
        return SQUAD_RANGE_TO_SHOW
