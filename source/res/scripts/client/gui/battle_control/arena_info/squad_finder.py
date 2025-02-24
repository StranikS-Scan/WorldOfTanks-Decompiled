# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_info/squad_finder.py
from collections import defaultdict, namedtuple
from constants import ARENA_GUI_TYPE
from gui.battle_control.arena_info import settings
from soft_exception import SoftException
from gui.shared.system_factory import registerSquadFinder, collectSquadFinder

class ISquadFinder(object):
    __slots__ = ()

    def clear(self):
        raise NotImplementedError

    def addVehicleInfo(self, team, prebattleID, vehicleID):
        raise NotImplementedError

    def getNumberOfSquadmen(self, team, prebattleID):
        raise NotImplementedError

    def getNumberOfSquads(self):
        raise NotImplementedError

    def findSquads(self):
        raise NotImplementedError

    def findSquadSizes(self):
        raise NotImplementedError


class EmptySquadFinder(ISquadFinder):
    __slots__ = ()

    def clear(self):
        pass

    def addVehicleInfo(self, team, prebattleID, vehicleID):
        pass

    def getNumberOfSquadmen(self, team, prebattleID):
        pass

    def getNumberOfSquads(self):
        pass

    def findSquads(self):
        return []

    def findSquadSizes(self):
        return []


class _SquadFinder(ISquadFinder):
    __slots__ = ('_prbStats',)

    def __init__(self, teams):
        super(_SquadFinder, self).__init__()
        self._prbStats = {team:defaultdict(set) for team in teams}

    def clear(self):
        for stats in self._prbStats.itervalues():
            stats.clear()

    def addVehicleInfo(self, team, prebattleID, vehicleID):
        if not prebattleID:
            return
        self._prbStats[team][prebattleID].add(vehicleID)

    def getNumberOfSquadmen(self, team, prebattleID):
        return len(self._prbStats[team][prebattleID])

    def getNumberOfSquads(self):
        raise NotImplementedError

    def findSquads(self):
        raise NotImplementedError

    def findSquadSizes(self):
        raise NotImplementedError

    @classmethod
    def _getSquadRange(cls):
        return settings.SQUAD_RANGE_TO_SHOW


SquadSizeDescription = namedtuple('SquadSizeDescription', ('teamID', 'squadID', 'squadSize'))

class TeamScopeNumberingFinder(_SquadFinder):
    __slots__ = ('_teamsSquadIndices',)

    def __init__(self, teams):
        super(TeamScopeNumberingFinder, self).__init__(teams)
        self._teamsSquadIndices = {team:{} for team in teams}

    def clear(self):
        for indices in self._teamsSquadIndices.itervalues():
            indices.clear()

        super(TeamScopeNumberingFinder, self).clear()

    def getNumberOfSquads(self):
        return sum((max(indices.itervalues()) for indices in self._teamsSquadIndices.itervalues() if indices))

    def findSquadSizes(self):
        squadRange = self._getSquadRange()
        for teamID, team in self._prbStats.iteritems():
            squadIndices = self._teamsSquadIndices[teamID]
            squads = [ item for item in team.iteritems() if len(item[1]) in squadRange ]
            if not squads:
                continue
            squads = sorted(squads, key=lambda item: item[0])
            for prebattleID, vehiclesIDs in squads:
                if prebattleID not in squadIndices:
                    if squadIndices:
                        squadIndices[prebattleID] = max(squadIndices.itervalues()) + 1
                    else:
                        squadIndices[prebattleID] = 1
                yield SquadSizeDescription(teamID, squadIndices[prebattleID], len(vehiclesIDs))

    def findSquads(self):
        squadRange = self._getSquadRange()
        for teamID, team in self._prbStats.iteritems():
            squadIndices = self._teamsSquadIndices[teamID]
            squads = [ item for item in team.iteritems() if len(item[1]) in squadRange ]
            if not squads:
                continue
            squads = sorted(squads, key=lambda item: item[0])
            for prebattleID, vehiclesIDs in squads:
                if prebattleID not in squadIndices:
                    if squadIndices:
                        squadIndices[prebattleID] = max(squadIndices.itervalues()) + 1
                    else:
                        squadIndices[prebattleID] = 1
                for vehicleID in vehiclesIDs:
                    yield (vehicleID, squadIndices[prebattleID])


class Comp7TeamScopeNumberingFinder(TeamScopeNumberingFinder):
    __slots__ = ()

    @classmethod
    def _getSquadRange(cls):
        return xrange(2, 8)


class ContinuousNumberingFinder(_SquadFinder):
    __slots__ = ('_squadIndices',)

    def __init__(self, teams):
        super(ContinuousNumberingFinder, self).__init__(teams)
        self._squadIndices = {}

    def clear(self):
        self._squadIndices.clear()
        super(ContinuousNumberingFinder, self).clear()

    def getNumberOfSquads(self):
        return max(self._squadIndices.itervalues()) if self._squadIndices else 0

    def findSquads(self):
        squadRange = self._getSquadRange()
        for _, team in self._prbStats.iteritems():
            for prebattleID, vehiclesIDs in team.iteritems():
                if not vehiclesIDs or len(vehiclesIDs) not in squadRange:
                    continue
                if prebattleID not in self._squadIndices:
                    if self._squadIndices:
                        self._squadIndices[prebattleID] = max(self._squadIndices.itervalues()) + 1
                    else:
                        self._squadIndices[prebattleID] = 1
                for vehicleID in vehiclesIDs:
                    yield (vehicleID, self._squadIndices[prebattleID])

    def findSquadSizes(self):
        raise SoftException('Deprecated class method called - code should not be reached')


registerSquadFinder(ARENA_GUI_TYPE.RANDOM, TeamScopeNumberingFinder)
registerSquadFinder(ARENA_GUI_TYPE.EPIC_RANDOM, TeamScopeNumberingFinder)
registerSquadFinder(ARENA_GUI_TYPE.EVENT_BATTLES, TeamScopeNumberingFinder)
registerSquadFinder(ARENA_GUI_TYPE.EPIC_BATTLE, TeamScopeNumberingFinder)
registerSquadFinder(ARENA_GUI_TYPE.BATTLE_ROYALE, TeamScopeNumberingFinder)
registerSquadFinder(ARENA_GUI_TYPE.MAPBOX, TeamScopeNumberingFinder)
registerSquadFinder(ARENA_GUI_TYPE.FALLOUT_MULTITEAM, ContinuousNumberingFinder)
registerSquadFinder(ARENA_GUI_TYPE.COMP7, Comp7TeamScopeNumberingFinder)

def createSquadFinder(arenaVisitor):
    teams = arenaVisitor.type.getTeamsOnArenaRange()
    guiVisitor = arenaVisitor.gui
    squadFinderClass = collectSquadFinder(guiVisitor.guiType)
    finder = squadFinderClass(teams) if squadFinderClass else EmptySquadFinder()
    return finder
