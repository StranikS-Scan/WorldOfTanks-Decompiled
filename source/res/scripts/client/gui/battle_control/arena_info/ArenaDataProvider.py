# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_info/ArenaDataProvider.py
from collections import defaultdict
import functools
import operator
from constants import ARENA_GUI_TYPE, TEAMS_IN_ARENA
from debug_utils import LOG_NOTE, LOG_WARNING, LOG_DEBUG
from gui.shared import fo_precache
from shared_utils import first
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO, VehicleArenaStatsDict, VehicleArenaStatsVO, VehicleArenaInteractiveStatsDict
from gui.battle_control.battle_constants import MULTIPLE_TEAMS_TYPE, PLAYER_GUI_PROPS
from gui.battle_control.arena_info import settings

class ArenaDataProvider(object):
    __slots__ = ('__playerTeam', '__playerVehicleID', '__vInfoVOs', '__vStatsVOs', '__viStatsVOs', '__prbStats', '__playersVIDs', '__weakref__', '__teamsOnArena', '__teamsVIStats', '__teamSquadIndices')

    def __init__(self, avatar=None):
        super(ArenaDataProvider, self).__init__()
        self.__playerTeam = avatar_getter.getPlayerTeam(avatar)
        self.__teamsOnArena = range(1, avatar_getter.getMaxTeamsOnArena(avatar) + 1)
        self.__playerVehicleID = avatar_getter.getPlayerVehicleID(avatar)
        self.__vInfoVOs = {}
        self.__vStatsVOs = VehicleArenaStatsDict()
        self.__prbStats = {}
        self.__playersVIDs = {}
        self.__viStatsVOs = VehicleArenaInteractiveStatsDict()
        self.__teamsVIStats = {}
        self.__teamSquadIndices = {}
        fo_precache.add(settings.UNKNOWN_CONTOUR_ICON_RES_PATH)

    def __del__(self):
        LOG_DEBUG('Deleted:', self)

    def clearInfo(self):
        self.__vInfoVOs.clear()
        self.__prbStats.clear()
        self.__playersVIDs.clear()
        self.__teamSquadIndices.clear()

    def clearStats(self):
        self.__vStatsVOs.clear()
        self.__viStatsVOs.clear()
        self.__teamsVIStats.clear()

    def clear(self):
        fo_precache.clear()
        self.clearInfo()
        self.clearStats()

    def defaultInfo(self):
        self.clearInfo()
        for team in self.getTeamsOnArena():
            self.__prbStats[team] = defaultdict(list)
            self.__teamSquadIndices[team] = {}

    def buildVehiclesData(self, vehicles, arenaGuiType):
        self.defaultInfo()
        for vID, vData in vehicles.iteritems():
            self.__addVehicleInfoVO(vID, VehicleArenaInfoVO(vID, **vData))

        self.__findSquads(arenaGuiType)

    def buildStatsData(self, stats):
        self.clearStats()
        for vID, vStats in stats.iteritems():
            self.__vStatsVOs[vID] = VehicleArenaStatsVO(vID, **vStats)

    def addVehicleInfo(self, vID, vInfo, arenaGuiType):
        vInfoVO = None
        if vID not in self.__vInfoVOs:
            vInfoVO = VehicleArenaInfoVO(vID, **vInfo)
            if self.__addVehicleInfoVO(vID, vInfoVO):
                self.__findSquads(arenaGuiType)
        else:
            LOG_WARNING('Vehicle already exists', self.__vInfoVOs[vID])
        return vInfoVO

    def updateVehicleInfo(self, vID, vInfo, arenaGuiType):
        vInfoVO = self.__vInfoVOs[vID]
        flags = vInfoVO.update(**vInfo)
        prebattleId = vInfoVO.prebattleID
        if flags & settings.INVALIDATE_OP.PREBATTLE_CHANGED:
            self.__updateStats(vInfoVO.team, prebattleId, vID)
            self.__findSquads(arenaGuiType)
        dbID = vInfoVO.player.accountDBID
        if dbID:
            self.__playersVIDs[dbID] = vID
        return (flags, vInfoVO)

    def updateVehicleStatus(self, vID, vInfo):
        vInfoVO = self.__vInfoVOs[vID]
        flags = vInfoVO.updateVehicleStatus(**vInfo)
        return (flags, vInfoVO)

    def updatePlayerStatus(self, vID, vInfo):
        vInfoVO = self.__vInfoVOs[vID]
        flags = vInfoVO.updatePlayerStatus(**vInfo)
        return (flags, vInfoVO)

    def updateVehicleStats(self, vID, vStats):
        vStatsVO = self.__vStatsVOs[vID]
        flags = vStatsVO.update(**vStats)
        return (flags, vStatsVO)

    def updateVehicleInteractiveStats(self, iStats):
        self.__viStatsVOs.clear()
        self.__teamsVIStats.clear()
        for (vID, _), iStat in iStats.iteritems():
            vStatsVO = self.__viStatsVOs[vID]
            vStatsVO.update(*iStat)
            vInfo = self.__vInfoVOs[vID]
            team = vInfo.team
            if team in self.__teamsVIStats:
                self.__teamsVIStats[team][vID] = vStatsVO
            self.__teamsVIStats[team] = {vID: vStatsVO}

    def isRequiredDataExists(self):
        return self.__checkRequiredData()

    def getTeamsOnArena(self):
        return self.__teamsOnArena

    def getAllyTeams(self):
        return (self.__playerTeam,)

    def getEnemyTeams(self):
        allyTeams = self.getAllyTeams()
        return filter(lambda t: t not in allyTeams, self.__teamsOnArena)

    def isEnemyTeam(self, team):
        return team not in self.getAllyTeams()

    def isAllyTeam(self, team):
        return team in self.getAllyTeams()

    def isMultipleTeams(self):
        return len(self.__teamsOnArena) > TEAMS_IN_ARENA.MIN_TEAMS

    def getMultiTeamsType(self):
        if self.isMultipleTeams():
            squadTeamNumber = 0
            for team in self.__prbStats.itervalues():
                squads = filter(lambda item: len(item[1]) in settings.SQUAD_RANGE_TO_SHOW, team.iteritems())
                if len(squads):
                    squadTeamNumber += 1

            if squadTeamNumber == 0:
                return MULTIPLE_TEAMS_TYPE.FFA
            if squadTeamNumber == len(self.__teamsOnArena):
                return MULTIPLE_TEAMS_TYPE.TDM
            return MULTIPLE_TEAMS_TYPE.MIXED
        else:
            return None

    def getMultiTeamsIndexes(self):
        lastTeamIdx = 0
        result = {}
        for team in self.__teamsOnArena:
            teamIdx = 0
            vInfoVO, _, _ = next(self._getVehiclesIterator(lambda v: v.team == team), (None, None, None))
            if vInfoVO is not None and vInfoVO.prebattleID > 0:
                lastTeamIdx += 1
                teamIdx = lastTeamIdx
            result[team] = teamIdx

        return result

    def getTeamIDsIterator(self):
        allyTeams = self.getAllyTeams()
        for teamIdx in self.__teamsOnArena:
            yield (teamIdx not in allyTeams, teamIdx)

    def getNumberOfTeam(self, enemy=False):
        if enemy:
            return first(self.getEnemyTeams())
        else:
            return self.__playerTeam

    def getPlayerVehicleID(self, forceUpdate=False):
        if forceUpdate and self.__playerVehicleID is None:
            self.__tryToGetRequiredData()
        return self.__playerVehicleID

    def getVehicleInfo(self, vID=None):
        if vID is None:
            vID = self.getPlayerVehicleID()
        try:
            result = self.__vInfoVOs[vID]
        except KeyError:
            result = VehicleArenaInfoVO(vID)

        return result

    def getVehicleStats(self, vID=None):
        if vID is None:
            vID = self.getPlayerVehicleID()
        return self.__vStatsVOs[vID]

    def getTeamStats(self, team=None):
        if team is None:
            team = self.__playerTeam
        return self.__teamsVIStats.get(team, {})

    def getVehIDsByPrebattleID(self, team, prebattleID):
        vehIDs = None
        if team in self.__prbStats and prebattleID in self.__prbStats[team]:
            vehIDs = list(self.__prbStats[team][prebattleID])
        return vehIDs

    def getPrbVehCount(self, team, prebattleID):
        vehIDs = self.getVehIDsByPrebattleID(team, prebattleID)
        return len(vehIDs) if vehIDs else 0

    def getVehicleInteractiveStats(self, vID=None):
        if vID is None:
            vID = self.getPlayerVehicleID()
        return self.__viStatsVOs[vID]

    def getPlayerGuiProps(self, vID, team):
        if team in self.getAllyTeams():
            if self.isSquadMan(vID=vID):
                return PLAYER_GUI_PROPS.squadman
            if self.isTeamKiller(vID=vID):
                return PLAYER_GUI_PROPS.teamKiller
            return PLAYER_GUI_PROPS.ally
        return PLAYER_GUI_PROPS.enemy

    def isSquadMan(self, vID, prebattleID=None):
        if prebattleID is None:
            if not self.__playerVehicleID:
                self.__playerVehicleID = avatar_getter.getPlayerVehicleID()
            if self.__playerVehicleID in self.__vInfoVOs:
                prebattleID = self.__vInfoVOs[self.__playerVehicleID].prebattleID
        return self.__getStateFlag(vID, 'isSquadMan', playerTeam=self.__playerTeam, prebattleID=prebattleID)

    def isTeamKiller(self, vID):
        return self.__getStateFlag(vID, 'isTeamKiller', playerTeam=self.__playerTeam)

    def isObserver(self, vID):
        return self.__getStateFlag(vID, 'isObserver')

    def getVehIDByAccDBID(self, dbID):
        try:
            vID = self.__playersVIDs[dbID]
        except KeyError:
            vID = 0

        return vID

    def getTeamIterator(self, teamIdx):
        return self._getVehiclesIterator(lambda v: v.team == teamIdx)

    def getVehiclesIterator(self, enemy=False, hasRespawns=False):
        if enemy:
            teams = self.getEnemyTeams()
        else:
            teams = self.getAllyTeams()
        return self._getVehiclesIterator(lambda v: v.team in teams, functools.partial(self._vehicleIteratorSortFunction, hasRespawns))

    def getAllVehiclesIterator(self):
        return self._getVehiclesIterator()

    def getAllVehiclesIteratorByTeamScore(self, hasRespawns=False):

        def sortByScore(x, y):
            xvInfoVO, xvStatsVO, xviStatsVO = x
            yvInfoVO, yvStatsVO, yviStatsVO = y
            teamStatsX = self.getTeamStats(xvInfoVO.team)
            teamStatsY = self.getTeamStats(yvInfoVO.team)
            teamScoreX = sum(map(operator.attrgetter('winPoints'), teamStatsX.itervalues()))
            teamScoreY = sum(map(operator.attrgetter('winPoints'), teamStatsY.itervalues()))
            res = cmp(teamScoreY, teamScoreX)
            return res if res else self._vehicleIteratorSortFunction(hasRespawns, x, y)

        return self._getVehiclesIterator(sortFunction=sortByScore)

    def getAllVehiclesIDsIterator(self):
        for vInfoVO, _, _ in self.getAllVehiclesIterator():
            yield vInfoVO.vehicleID

    def getAllVehiclesIDs(self):
        return list(self.getAllVehiclesIDsIterator())

    def getVehiclesIDsIterator(self, enemy=False):
        for vInfoVO, _, _ in self.getVehiclesIterator(enemy):
            yield vInfoVO.vehicleID

    def getVehiclesIDs(self, enemy=False):
        return list(self.getVehiclesIDsIterator(enemy))

    def _vehicleIteratorSortFunction(self, hasRespawns, x, y):
        xvInfoVO, xvStatsVO, xviStatsVO = x
        yvInfoVO, yvStatsVO, yviStatsVO = y
        result = cmp(xvInfoVO.team, yvInfoVO.team)
        if result:
            return result
        if hasRespawns:
            result = cmp(xviStatsVO.stopRespawn, yviStatsVO.stopRespawn)
            if result:
                return result
        else:
            result = cmp(yvInfoVO.isAlive(), xvInfoVO.isAlive())
            if result:
                return result
        result = cmp(xvInfoVO.vehicleType, yvInfoVO.vehicleType)
        return result if result else cmp(xvInfoVO.player, yvInfoVO.player)

    def _getVehiclesIterator(self, filterPredicate=None, sortFunction=None):
        if filterPredicate is None:
            data = self.__vInfoVOs.itervalues()
        else:
            data = filter(filterPredicate, self.__vInfoVOs.itervalues())
        data = map(lambda vInfoVO: (vInfoVO, self.__vStatsVOs[vInfoVO.vehicleID], self.__viStatsVOs[vInfoVO.vehicleID]), data)
        if sortFunction is None:
            sortedData = sorted(data, cmp=functools.partial(self._vehicleIteratorSortFunction, False))
        else:
            sortedData = sorted(data, cmp=sortFunction)
        for vehicleData in sortedData:
            yield vehicleData

        return

    def __findSquads(self, arenaGuiType):
        if arenaGuiType not in (ARENA_GUI_TYPE.RANDOM,
         ARENA_GUI_TYPE.FALLOUT_CLASSIC,
         ARENA_GUI_TYPE.FALLOUT_MULTITEAM,
         ARENA_GUI_TYPE.EVENT_BATTLES):
            return
        for teamID in self.__prbStats:
            team = self.__prbStats[teamID]
            squadIndices = self.__teamSquadIndices[teamID]
            squads = filter(lambda item: len(item[1]) in settings.SQUAD_RANGE_TO_SHOW, team.iteritems())
            if len(squads):
                squads = sorted(squads, key=lambda item: item[0])
                for prbID, vIDs in squads:
                    if squadIndices[prbID] == 0:
                        squadIndices[prbID] = max(squadIndices.values()) + 1
                    for vID in vIDs:
                        vInfoVO = self.__vInfoVOs[vID]
                        vInfoVO.squadIndex = squadIndices[prbID]
                        vInfoVO.updatePlayerStatus(isSquadMan=True)

    def __addVehicleInfoVO(self, vID, vInfoVO):
        dbID = vInfoVO.player.accountDBID
        hasPrbID = False
        self.__vInfoVOs[vID] = vInfoVO
        if dbID:
            self.__playersVIDs[dbID] = vID
        prebattleID = vInfoVO.prebattleID
        if prebattleID > 0:
            self.__updateStats(vInfoVO.team, prebattleID, vID)
            hasPrbID = True
        return hasPrbID

    def __getStateFlag(self, vID, flagName, **kwargs):
        result = False
        if vID in self.__vInfoVOs:
            result = operator.methodcaller(flagName, **kwargs)(self.__vInfoVOs[vID])
        return result

    def __checkRequiredData(self):
        result = self.__playerTeam > 0 and self.__playerVehicleID > 0
        return result or self.__tryToGetRequiredData()

    def __tryToGetRequiredData(self):
        successful = True
        self.__playerTeam = avatar_getter.getPlayerTeam()
        if not self.__playerTeam:
            successful = False
            LOG_NOTE("Player's team not found.")
        self.__playerVehicleID = avatar_getter.getPlayerVehicleID()
        if not self.__playerVehicleID:
            successful = False
            LOG_NOTE("Player's vehicle ID not found.")
        if not successful:
            playerName = avatar_getter.getPlayerName()
            LOG_NOTE('Uses slow player search by name')
            for vo in self.__vInfoVOs.itervalues():
                if vo.player.name == playerName:
                    self.__playerTeam = vo.team
                    self.__playerVehicleID = vo.vehicleID
                    successful = True
                    break

        return successful

    def __updateStats(self, team, prebattleID, vID):
        if prebattleID not in self.__prbStats[team]:
            self.__prbStats[team][prebattleID] = set()
            self.__teamSquadIndices[team][prebattleID] = 0
        self.__prbStats[team][prebattleID].add(vID)
