# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/arena_components/player_data_component.py
from arena_component_system.client_arena_component_system import ClientArenaComponent
import Event
import player_ranks
from debug_utils import LOG_DEBUG_DEV
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from gui.battle_control import avatar_getter
from constants import ARENA_SYNC_OBJECTS, PLAYER_RANK

class PlayerDataComponent(ClientArenaComponent):
    playerGroups = property(lambda self: self.__getPlayerGroups())
    playerRank = property(lambda self: self.__getPlayerRank())
    playerGroupsEnabled = property(lambda self: self.__playerGroupsEnabled)

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self.__playerGroupsEnabled = componentSystem.arenaType.numPlayerGroups > 0
        LOG_DEBUG_DEV('PlayerDataComponent.__playerGroupsEnabled ', self.__playerGroupsEnabled, componentSystem.arenaType.numPlayerGroups > 0)
        self.onPlayerGroupsUpdated = Event.Event(self._eventManager)
        arena = componentSystem.arena()
        self.__playerIngameRanksEnabled = arena.hasBonusCap(BONUS_CAPS.PLAYER_RANK_MECHANICS)
        self.__playerRank = None
        self.onCrewRolesFactorUpdated = Event.Event(self._eventManager)
        self.onPlayerRankUpdated = Event.Event(self._eventManager)
        return

    def activate(self):
        super(PlayerDataComponent, self).activate()
        if self.__playerGroupsEnabled:
            self.addSyncDataCallback(ARENA_SYNC_OBJECTS.PLAYER_GROUP, 'playerGroups', self._vehiclePlayerGroupsUpdated)
        if self.__playerIngameRanksEnabled:
            self.addSyncDataCallback(ARENA_SYNC_OBJECTS.PLAYER_RANK, 'ranksByTeam', self.__onTeamRanksUpdated)

    def deactivate(self):
        super(PlayerDataComponent, self).deactivate()
        if self.__playerGroupsEnabled:
            self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.PLAYER_GROUP, 'playerGroups', self._vehiclePlayerGroupsUpdated)
        if self.__playerIngameRanksEnabled:
            self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.PLAYER_RANK, 'ranksByTeam', self.__onTeamRanksUpdated)

    def playerIngameRanksEnabled(self):
        return self.__playerIngameRanksEnabled

    def getTresholdForRanks(self):
        xpTresholdForRanks = []
        if not self.__playerIngameRanksEnabled:
            return
        else:
            defaultAlgorithmSettings = player_ranks.getSettings().algorithm
            for rank in range(PLAYER_RANK.DEFAULT_RANK, PLAYER_RANK.MAX_RANK + 1):
                if rank == PLAYER_RANK.NO_RANK:
                    xpTresholdForRanks.append(0)
                    continue
                rankSettings = defaultAlgorithmSettings.byRank.get(rank, None)
                if rankSettings is not None:
                    xpTresholdForRanks.append(rankSettings.threshold)

            return xpTresholdForRanks

    def getPlayerGroupForVehicle(self, vId):
        playerGroups = self.__getPlayerGroups()
        return playerGroups.get(vId, 1)

    def getPlayerGroupForPlayer(self):
        return self.getPlayerGroupForVehicle(avatar_getter.getPlayerVehicleID())

    def _vehiclePlayerGroupsUpdated(self, args):
        arena = avatar_getter.getArena()
        if arena is not None:
            key = 'playerGroup'
            gameModeStats = dict(((vehID, {key: playerGroup}) for vehID, playerGroup in args.iteritems()))
            arena.updateGameModeSpecificStats(True, gameModeStats)
        self.onPlayerGroupsUpdated(args)
        return

    def __getPlayerGroups(self):
        if not self.__playerGroupsEnabled:
            return None
        else:
            playerGroups = self.getSyncDataObjectData(ARENA_SYNC_OBJECTS.PLAYER_GROUP, 'playerGroups')
            return playerGroups

    def __getPlayerRank(self):
        if self.__playerRank is not None:
            return self.__playerRank
        else:
            playerVehicleID = avatar_getter.getPlayerVehicleID()
            if self.__playerRank is None and playerVehicleID is not None:
                ranksPerTeam = self.getSyncDataObjectData(ARENA_SYNC_OBJECTS.PLAYER_RANK, 'ranksByTeam')
                if ranksPerTeam is not None:
                    teamranks = ranksPerTeam.get(avatar_getter.getPlayerTeam(), None)
                    if teamranks is not None:
                        self.__playerRank = teamranks.get(playerVehicleID, None)
            return self.__playerRank

    def __onTeamRanksUpdated(self, args):
        arena = avatar_getter.getArena()
        playerVehicleId = avatar_getter.getPlayerVehicleID()
        LOG_DEBUG_DEV('__onTeamRanksUpdated', args)
        if arena is not None:
            key = 'playerRank'
            for _, ranksPerTeam in args.iteritems():
                if playerVehicleId in ranksPerTeam:
                    self.__playerRank = ranksPerTeam[playerVehicleId]
                gameModeStats = dict(((vehID, {key: rank}) for vehID, rank in ranksPerTeam.iteritems()))
                arena.updateGameModeSpecificStats(False, gameModeStats)

        return
