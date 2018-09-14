# Embedded file name: scripts/client/gui/battle_control/arena_info/ArenaDataProvider.py
from collections import defaultdict
from constants import ARENA_GUI_TYPE
from debug_utils import LOG_NOTE, LOG_WARNING, LOG_DEBUG
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO, VehicleArenaStatsDict, VehicleArenaStatsVO
from gui.battle_control.arena_info.settings import SQUAD_RANGE_TO_SHOW, TEAM_RANGE, invertTeam

class ArenaDataProvider(object):
    __slots__ = ('__playerTeam', '__playerVehicleID', '__vInfoVOs', '__vStatsVOs', '__prbStats', '__playersVIDs')

    def __init__(self):
        super(ArenaDataProvider, self).__init__()
        self.__playerTeam = avatar_getter.getPlayerTeam()
        self.__playerVehicleID = avatar_getter.getPlayerVehicleID()
        self.__vInfoVOs = {}
        self.__vStatsVOs = VehicleArenaStatsDict()
        self.__prbStats = {}
        self.__playersVIDs = {}

    def __del__(self):
        LOG_DEBUG('Deleted:', self)

    def clearInfo(self):
        self.__vInfoVOs.clear()
        self.__prbStats.clear()
        self.__playersVIDs.clear()

    def clearStats(self):
        self.__vStatsVOs.clear()

    def clear(self):
        self.clearInfo()
        self.clearStats()

    def defaultInfo(self):
        self.clearInfo()
        for team in TEAM_RANGE:
            self.__prbStats[team] = defaultdict(list)

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

    def updateVehicleInfo(self, vID, vInfo):
        vInfoVO = self.__vInfoVOs[vID]
        flags = vInfoVO.update(**vInfo)
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

    def isRequiredDataExists(self):
        return self.__checkRequiredData()

    def getNumberOfTeam(self, enemy = False):
        if enemy:
            return invertTeam(self.__playerTeam)
        return self.__playerTeam

    def getPlayerVehicleID(self):
        return self.__playerVehicleID

    def getVehicleInfo(self, vID = None):
        if vID is None:
            vID = self.getPlayerVehicleID()
        try:
            result = self.__vInfoVOs[vID]
        except KeyError:
            result = VehicleArenaInfoVO(vID)

        return result

    def getVehicleStats(self, vID = None):
        return self.__vStatsVOs[vID]

    def isSquadMan(self, vID, prebattleID = None):
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

    def getTeamIterator(self, enemy = False):
        team = self.getNumberOfTeam(enemy)
        if not team:
            LOG_NOTE('Team not found')
            data = []
        else:
            data = sorted(filter(lambda vInfoVO: vInfoVO.team == team, self.__vInfoVOs.itervalues()))
        for vInfoVO in data:
            yield (vInfoVO, self.__vStatsVOs[vInfoVO.vehicleID])

    def getVehiclesIDsIterator(self, enemy = False):
        team = self.getNumberOfTeam(enemy)
        if not team:
            LOG_NOTE('Team not found')
            data = []
        else:
            data = sorted(filter(lambda vInfoVO: vInfoVO.team == team, self.__vInfoVOs.itervalues()))
        for vInfoVO in data:
            yield vInfoVO.vehicleID

    def getVehiclesIDs(self, enemy = False):
        return list(self.getVehiclesIDsIterator(enemy))

    def __findSquads(self, arenaGuiType):
        if arenaGuiType not in (ARENA_GUI_TYPE.RANDOM, ARENA_GUI_TYPE.EVENT_BATTLES):
            return
        for team in self.__prbStats.iterkeys():
            squads = filter(lambda item: len(item[1]) in SQUAD_RANGE_TO_SHOW, self.__prbStats[team].iteritems())
            if len(squads):
                squads = sorted(squads, key=lambda item: item[0])
                for index, (prbID, vIDs) in enumerate(squads):
                    squadsIndex = index + 1
                    for vID in vIDs:
                        vInfoVO = self.__vInfoVOs[vID]
                        vInfoVO.squadIndex = squadsIndex
                        vInfoVO.updatePlayerStatus(isSquadMan=True)

    def __addVehicleInfoVO(self, vID, vInfoVO):
        dbID = vInfoVO.player.accountDBID
        hasPrbID = False
        self.__vInfoVOs[vID] = vInfoVO
        if dbID:
            self.__playersVIDs[dbID] = vID
        prebattleID = vInfoVO.prebattleID
        if prebattleID > 0:
            self.__prbStats[vInfoVO.team][prebattleID].append(vID)
            hasPrbID = True
        return hasPrbID

    def __getStateFlag(self, vID, flagName, **kwargs):
        result = False
        if vID in self.__vInfoVOs:
            result = getattr(self.__vInfoVOs[vID], flagName)(**kwargs)
        return result

    def __checkRequiredData(self):
        result = self.__playerTeam > 0 and self.__playerVehicleID > 0
        if not result:
            requestToFind = False
            self.__playerTeam = avatar_getter.getPlayerTeam()
            if not self.__playerTeam:
                requestToFind = True
                LOG_NOTE("Player's team not found.")
            self.__playerVehicleID = avatar_getter.getPlayerVehicleID()
            if not self.__playerVehicleID:
                requestToFind = True
                LOG_NOTE("Player's vehicle ID not found.")
            if not requestToFind:
                return
            playerName = avatar_getter.getPlayerName()
            LOG_NOTE('Uses slow player search by name')
            for vo in self.__vInfoVOs.itervalues():
                if vo.player.name == playerName:
                    self.__playerTeam = vo.team
                    self.__playerVehicleID = vo.vehicleID
                    result = True
                    break

        return result
