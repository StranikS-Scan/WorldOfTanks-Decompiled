# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/ArenaInfoComp7Component.py
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import Comp7Keys
from helpers import dependency
from script_component.ScriptComponent import ScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider

class ArenaInfoComp7Component(ScriptComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onEnterWorld(self, *args):
        super(ArenaInfoComp7Component, self).onEnterWorld(*args)
        arena = avatar_getter.getArena()
        if arena is not None:
            arena.onNewVehicleListReceived += self.__onNewVehicleListReceived
            arena.onVehicleAdded += self.__onVehicleAdded
        self.__invalidateRanks()
        return

    def onLeaveWorld(self):
        arena = avatar_getter.getArena()
        if arena is not None:
            arena.onNewVehicleListReceived -= self.__onNewVehicleListReceived
            arena.onVehicleAdded -= self.__onVehicleAdded
        super(ArenaInfoComp7Component, self).onLeaveWorld()
        return

    def set_ranks(self, prev):
        self.__invalidateRanks()

    def __invalidateRanks(self):
        vInfos = self.__sessionProvider.getArenaDP().getVehiclesInfoIterator()
        ranks = {vInfo.vehicleID:self.ranks[vInfo.vehicleID] for vInfo in vInfos if vInfo.vehicleID in self.ranks}
        self.__updateGameModeStats(ranks)

    def __invalidateRank(self, vehicleID):
        if vehicleID in self.ranks:
            ranks = {vehicleID: self.ranks[vehicleID]}
            self.__updateGameModeStats(ranks)

    def __onNewVehicleListReceived(self):
        if self._isAvatarReady:
            self.__invalidateRanks()

    def __onVehicleAdded(self, vehicleID):
        if self._isAvatarReady:
            self.__invalidateRank(vehicleID)

    @staticmethod
    def __updateGameModeStats(ranks):
        arena = avatar_getter.getArena()
        if not arena:
            return
        stats = {vehID:{Comp7Keys.RANK: rank} for vehID, rank in ranks.iteritems()}
        if stats:
            arena.onGameModeSpecificStats(isStatic=True, stats=stats)
