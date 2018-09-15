# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/arena_components/player_data_component.py
import BigWorld
from arena_component_system.client_arena_component_system import ClientArenaComponent
from constants import ARENA_SYNC_OBJECTS
import Event
from debug_utils import LOG_DEBUG_DEV

class PlayerDataComponent(ClientArenaComponent):
    playerGroups = property(lambda self: self.__getPlayerGroups())

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self.__playerGroupsEnabled = componentSystem.arenaType.numPlayerGroups > 0
        LOG_DEBUG_DEV('PlayerDataComponent.__playerGroupsEnabled ', self.__playerGroupsEnabled, componentSystem.arenaType.numPlayerGroups > 0)
        if self.__playerGroupsEnabled:
            self.addSyncDataCallback(ARENA_SYNC_OBJECTS.PLAYER_GROUP, 'playerGroups', self.__vehiclePlayerGroupsUpdated)
        self.onPlayerGroupsUpdated = Event.Event(self._eventManager)

    def destroy(self):
        if self.__playerGroupsEnabled:
            self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.PLAYER_GROUP, 'playerGroups', self.__vehiclePlayerGroupsUpdated)

    def __getPlayerGroups(self):
        if not self.__playerGroupsEnabled:
            return None
        else:
            playerGroups = self.getSyncDataObjectData(ARENA_SYNC_OBJECTS.PLAYER_GROUP, 'playerGroups')
            return playerGroups

    def __vehiclePlayerGroupsUpdated(self, args):
        player = BigWorld.player()
        arena = getattr(player, 'arena', None)
        if arena is not None:
            key = 'playerGroup'
            gameModeStats = dict(((vehID, {key: playerGroup}) for vehID, playerGroup in args.iteritems()))
            arena.onGameModeSpecifcStats(True, gameModeStats)
        self.onPlayerGroupsUpdated(args)
        return
