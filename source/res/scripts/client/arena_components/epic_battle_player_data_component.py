# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/arena_components/epic_battle_player_data_component.py
from collections import defaultdict
from arena_components.player_data_component import PlayerDataComponent
from constants import ARENA_SYNC_OBJECTS, SECTOR_STATE, ARENA_PERIOD
from PlayerEvents import g_playerEvents
from debug_utils import LOG_CURRENT_EXCEPTION
import Event
import BigWorld
from gui.battle_control import avatar_getter

class EpicBattlePlayerDataComponent(PlayerDataComponent):
    playerLives = property(lambda self: self.__getPlayerLives())
    respawnLane = property(lambda self: self.__getRespawnLane())
    physicalLane = property(lambda self: self.__physicalLane)
    physicalSectorGroup = property(lambda self: self.__physicalSectorGroup)
    playerXP = property(lambda self: self.__playerXP)
    reinforcementTimer = property(lambda self: self.__nextReinforcmentTimer)
    playerSectorID = property(lambda self: self.__getPlayerSectorID())
    hqSectorID = property(lambda self: self.__getHQSectorID())

    def __init__(self, componentSystem):
        super(EpicBattlePlayerDataComponent, self).__init__(componentSystem)
        self.addSyncDataCallback(ARENA_SYNC_OBJECTS.SECTOR, 'playerSectorInfo', self.__vehiclePlayerSectorUpdated)
        self.addSyncDataCallback(ARENA_SYNC_OBJECTS.RESPAWN, 'nextLiveUpdateTimer', self.__onLiveUpdateTimerUpdated)
        self.addSyncDataCallback(ARENA_SYNC_OBJECTS.RESPAWN, 'livesByTeamGroup', self.__onLivesPerTeamGroupUpdated)
        self.addSyncDataCallback(ARENA_SYNC_OBJECTS.RESPAWN, 'respawnOffsets', self.__onRespawnOffsetsUpdated)
        self.addSyncDataCallback(ARENA_SYNC_OBJECTS.RESPAWN, 'outOfLives', self.__onPlayerOutOfLivesAdded)
        self.addSyncDataCallback(ARENA_SYNC_OBJECTS.RESPAWN, 'outOfLives_d', self.__onPlayerOutOfLivesDeleted)
        self.addSyncDataCallback(ARENA_SYNC_OBJECTS.FRONT_LINE, 'CoM', self.__onFrontlineCenterOfMassUpdated)
        self.__playerLives = -1
        self.__respawnLane = None
        self.__physicalLane = None
        self.__physicalSectorGroup = None
        self.__playerSectorID = -1
        self.__nextReinforcmentTimer = None
        self.__lastTeamLives = defaultdict(int)
        self.__playerXP = 0
        self.__hqSectorID = None
        self.onPlayerRespawnLaneUpdated = Event.Event(self._eventManager)
        self.onPlayerPhysicalLaneUpdated = Event.Event(self._eventManager)
        self.onReinforcementTimerUpdated = Event.Event(self._eventManager)
        self.onReinforcementsArrived = Event.Event(self._eventManager)
        self.onPlayerGroupsChanged = Event.Event(self._eventManager)
        self.onPlayerXPUpdated = Event.Event(self._eventManager)
        self.onFrontlineCenterUpdated = Event.Event(self._eventManager)
        self.onRespawnOffsetsUpdated = Event.Event(self._eventManager)
        g_playerEvents.onAvatarBecomePlayer += self.setPlayerLaneByPlayerGroups
        return

    def destroy(self):
        super(EpicBattlePlayerDataComponent, self).destroy()
        self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.SECTOR, 'playerSectorInfo', self.__vehiclePlayerSectorUpdated)
        self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.RESPAWN, 'nextLiveUpdateTimer', self.__onLiveUpdateTimerUpdated)
        self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.RESPAWN, 'livesByTeamGroup', self.__onLivesPerTeamGroupUpdated)
        self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.RESPAWN, 'respawnOffsets', self.__onRespawnOffsetsUpdated)
        self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.RESPAWN, 'outOfLives', self.__onPlayerOutOfLivesAdded)
        self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.RESPAWN, 'outOfLives_d', self.__onPlayerOutOfLivesDeleted)
        self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.FRONT_LINE, 'CoM', self.__onFrontlineCenterOfMassUpdated)
        g_playerEvents.onAvatarBecomePlayer -= self.setPlayerLaneByPlayerGroups

    def getPlayerLivesForTeam(self, teamId):
        lives = 0
        livesPerTeamAndGroup = self.getSyncDataObjectData(ARENA_SYNC_OBJECTS.RESPAWN, 'livesByTeamGroup')
        if livesPerTeamAndGroup is not None:
            for teamAndGroup, teamLives in livesPerTeamAndGroup.iteritems():
                if teamAndGroup[0] == teamId:
                    lives += teamLives

        return lives

    def getPlayersForTeamAndGroup(self, teamId, groupId):
        playersPerTeamAndGroup = self.getSyncDataObjectData(ARENA_SYNC_OBJECTS.PLAYER_GROUP, 'numPlayersPerGroup')
        if playersPerTeamAndGroup is not None:
            for key, count in playersPerTeamAndGroup.iteritems():
                if key[0] == teamId and key[1] == groupId:
                    return count

        return 0

    def getPlayerLivesForTeamAndGroup(self, teamId, groupId):
        livesPerTeamAndGroup = self.getSyncDataObjectData(ARENA_SYNC_OBJECTS.RESPAWN, 'livesByTeamGroup')
        if livesPerTeamAndGroup is None:
            return 0
        else:
            livesPerTeam = livesPerTeamAndGroup.get((teamId, groupId), 0)
            return livesPerTeam

    def getFrontlineCenters(self):
        centerOfMass = self.getSyncDataObjectData(ARENA_SYNC_OBJECTS.FRONT_LINE, 'CoM')
        return centerOfMass

    def getRespawnOffsetsForTeam(self, team):
        respawnOffsets = self.getSyncDataObjectData(ARENA_SYNC_OBJECTS.RESPAWN, 'respawnOffsets')
        if respawnOffsets is None:
            return 0.0
        else:
            offsetsForTeam = respawnOffsets.get(team, None)
            return offsetsForTeam

    def getPlayerInHQSector(self):
        return self.__hqSectorID == self.physicalSectorGroup

    def getPhysicalSectorForAllVehicles(self):
        vehicleSectorIDs = self.getSyncDataObjectData(ARENA_SYNC_OBJECTS.SECTOR, 'playerSectorInfo')
        return vehicleSectorIDs

    def getPhysicalSectorForVehicle(self, vehId):
        vehicleSectorIDs = self.getSyncDataObjectData(ARENA_SYNC_OBJECTS.SECTOR, 'playerSectorInfo')
        sectorID, _ = vehicleSectorIDs.get(vehId, (0, 0))
        return sectorID

    def getPhysicalLaneForVehicle(self, vehId):
        vehicleSectorIDs = self.getSyncDataObjectData(ARENA_SYNC_OBJECTS.SECTOR, 'playerSectorInfo')
        _, groupID = vehicleSectorIDs.get(vehId, (0, 0))
        return groupID

    def setPhysicalLane(self, lane, groupID, force=False):
        if self.__physicalLane != lane or self.__physicalSectorGroup != groupID or force:
            self.__physicalLane = lane
            self.__physicalSectorGroup = groupID
            self.onPlayerPhysicalLaneUpdated(lane)

    def setPlayerXP(self, xp):
        self.__playerXP = xp
        self.onPlayerXPUpdated(xp)

    def setPlayerLaneByPlayerGroups(self):
        playerId = avatar_getter.getPlayerVehicleID()
        playerGroups = self.playerGroups
        if playerGroups and playerId is not 0 and playerId in playerGroups:
            self.__respawnLane = playerGroups[playerId]
            self.onPlayerRespawnLaneUpdated(self.__respawnLane)
            self.setPhysicalLane(self.__respawnLane, self.__physicalSectorGroup, force=True)

    def getGameTimeToAddPerCapture(self, idInPlayerGroup):
        timesToAdd = self.getSyncDataObjectData(ARENA_SYNC_OBJECTS.SECTOR, 'gameTimeToAddPerCapture')
        if timesToAdd is not None:
            try:
                return timesToAdd[idInPlayerGroup - 1]
            except (TypeError, IndexError, KeyError):
                LOG_CURRENT_EXCEPTION(["Failed to get 'gameTimeToAddPerCapture' from arena sector sync data for zone '{}'!".format(idInPlayerGroup), timesToAdd])

        return 0.0

    def getGameTimeToAddWhenAllCaptured(self):
        time = self.getSyncDataObjectData(ARENA_SYNC_OBJECTS.SECTOR, 'gameTimeToAddWhenAllCaptured')
        return time if time is not None else 0.0

    def getPlayerGroupForVehicle(self, vId):
        return self.getPhysicalLaneForVehicle(vId)

    def getPlayerGroupForPlayer(self):
        return self.__physicalLane

    def _vehiclePlayerGroupsUpdated(self, args):
        self.__respawnLane = None
        arena = avatar_getter.getArena()
        if arena is not None:
            key = 'playerGroup'
            gameModeStats = dict(((vehID, {key: playerGroup}) for vehID, playerGroup in args.iteritems()))
            arena.onGameModeSpecifcStats(False, gameModeStats)
        self.onPlayerGroupsUpdated(args)
        playerId = avatar_getter.getPlayerVehicleID()
        if playerId is not 0 and playerId in args:
            self.__respawnLane = args[playerId]
            self.onPlayerRespawnLaneUpdated(self.__respawnLane)
        return

    def __getPlayerLives(self):
        if self.__playerLives == -1:
            livesPerPlayer = self.getSyncDataObjectData(ARENA_SYNC_OBJECTS.RESPAWN, 'vehLives')
            if livesPerPlayer is not None:
                self.__playerLives = livesPerPlayer.get(BigWorld.player().playerVehicleID, -1)
        return self.__playerLives

    def __getRespawnLane(self):
        if self.__respawnLane is None:
            if self.playerGroups is not None:
                self.__respawnLane = self.playerGroups.get(BigWorld.player().playerVehicleID, None)
        return self.__respawnLane

    def __getPlayerSectorID(self):
        if not self.respawnLane or not self.hqSectorID:
            return self.__playerSectorID
        sectorGroups = BigWorld.player().arena.componentSystem.sectorComponent.sectorGroups
        playerSectorID = -1
        for groupID, group in sectorGroups.items():
            if group.playerGroup == self.respawnLane and group.state == SECTOR_STATE.OPEN:
                playerSectorID = groupID
                break

        if playerSectorID < 0 and sectorGroups[self.hqSectorID].state == SECTOR_STATE.OPEN:
            playerSectorID = self.hqSectorID
        if playerSectorID < 0:
            for groupID, group in sectorGroups.items():
                if group.playerGroup == self.__physicalSectorGroup and group.state in (SECTOR_STATE.TRANSITION, SECTOR_STATE.BOMBING, SECTOR_STATE.CAPTURED):
                    playerSectorID = groupID
                    break

        if playerSectorID != -1 and playerSectorID != self.__playerSectorID:
            self.__playerSectorID = playerSectorID
        return self.__playerSectorID

    def __getHQSectorID(self):
        if self.__hqSectorID is None:
            sectorGroups = BigWorld.player().arena.componentSystem.sectorComponent.sectorGroups
            for groupID in sectorGroups:
                group = sectorGroups[groupID]
                if group.numSubSectors > 1:
                    self.__hqSectorID = groupID
                    break

        return self.__hqSectorID

    def __onLiveUpdateTimerUpdated(self, args):
        self.__nextReinforcmentTimer = args
        self.onReinforcementTimerUpdated(args)

    def __vehiclePlayerSectorUpdated(self, args):
        playerVehicleId = avatar_getter.getPlayerVehicleID()
        arena = avatar_getter.getArena()
        if not arena:
            return
        if playerVehicleId in args:
            _, group = args[playerVehicleId]
            if self.__physicalLane != group:
                self.__physicalLane = group
                self.onPlayerPhysicalLaneUpdated(group)
        gameModeStats = dict(((vehID, {'playerGroup': group,
          'physicalSector': sectorID}) for vehID, (sectorID, group) in args.iteritems()))
        self.onPlayerGroupsUpdated(args)
        arena.onGameModeSpecifcStats(False, gameModeStats)

    def __onLivesPerTeamGroupUpdated(self, args):
        if BigWorld.player().arena.period != ARENA_PERIOD.BATTLE:
            return
        changedTemIds = []
        for teamAndGroup, _ in args.iteritems():
            if teamAndGroup[0] not in changedTemIds:
                changedTemIds.append(teamAndGroup[0])

        for teamId in changedTemIds:
            if self.__lastTeamLives[teamId] > 0 and self.getPlayerLivesForTeam(teamId) > self.__lastTeamLives[teamId]:
                self.onReinforcementsArrived(teamId)
            self.__lastTeamLives[teamId] = self.getPlayerLivesForTeam(teamId)

    def __onFrontlineCenterOfMassUpdated(self, args):
        self.onFrontlineCenterUpdated(args)

    def __onRespawnOffsetsUpdated(self, args):
        self.onRespawnOffsetsUpdated(args)

    def __onPlayerOutOfLivesAdded(self, args):
        self.__updatePlayerOutOfLives(args, False)

    def __onPlayerOutOfLivesDeleted(self, args):
        self.__updatePlayerOutOfLives(args, True)

    def __updatePlayerOutOfLives(self, playerList, hasRespawns):
        arena = avatar_getter.getArena()
        if not arena:
            return
        gameModeStats = dict(((vehID, {'hasRespawns': hasRespawns}) for vehID in playerList))
        arena.onGameModeSpecifcStats(False, gameModeStats)
