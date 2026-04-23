# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/ArenaInfoComp7Component.py
from ArenaInfoComp7BaseComponent import ArenaInfoComp7BaseComponent
from comp7_core.gui.comp7_core_constants import BATTLE_CTRL_ID
from comp7.gui.battle_control.arena_info.arena_vos import Comp7Keys
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class ArenaInfoComp7Component(ArenaInfoComp7BaseComponent, IArenaVehiclesController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(ArenaInfoComp7Component, self).__init__()
        self.__invalidateRanks()
        self.__sessionProvider.addArenaCtrl(self)

    def getCtrlScope(self):
        return _SCOPE.VEHICLES

    def invalidateVehiclesInfo(self, arenaDP):
        self.__invalidateRanks()

    def onLeaveWorld(self):
        self.__sessionProvider.removeArenaCtrl(self)
        arena = avatar_getter.getArena()
        if arena is not None:
            arena.onNewVehicleListReceived -= self.__onNewVehicleListReceived
            arena.onVehicleAdded -= self.__onVehicleAdded
        super(ArenaInfoComp7Component, self).onLeaveWorld()
        return

    def set_ranks(self, prev):
        self.__invalidateRanks()

    def set_bannedVehicles(self, _):
        if self._isAvatarReady:
            self.__updateBannedVehicles()

    def set_vehicleBanList(self, _):
        if self._isAvatarReady:
            self.__updateVehicleBanList()

    def _onAvatarReady(self):
        self.__sessionProvider.removeArenaCtrl(self)
        arena = avatar_getter.getArena()
        if arena is not None:
            arena.onNewVehicleListReceived += self.__onNewVehicleListReceived
            arena.onVehicleAdded += self.__onVehicleAdded
        self.__invalidateRanks()
        self.__updateBannedVehicles()
        self.__updateVehicleBanList()
        return

    def __invalidateRanks(self):
        vInfos = self.__sessionProvider.getArenaDP().getVehiclesInfoIterator()
        ranks = {vInfo.vehicleID:self.ranks[vInfo.vehicleID] for vInfo in vInfos if vInfo.vehicleID in self.ranks}
        self.__updateGameModeStats(ranks)

    def __invalidateRank(self, vehicleID):
        if vehicleID in self.ranks:
            ranks = {vehicleID: self.ranks[vehicleID]}
            self.__updateGameModeStats(ranks)

    def __onNewVehicleListReceived(self):
        self.__invalidateRanks()

    def __onVehicleAdded(self, vehicleID):
        if self._isAvatarReady:
            self.__invalidateRank(vehicleID)

    @staticmethod
    def __updateGameModeStats(ranks):
        arena = avatar_getter.getArena()
        if not arena:
            return
        stats = dict()
        for vehID, rank in ranks.iteritems():
            stats[vehID] = {Comp7Keys.RANK: rank['divisionRank'],
             Comp7Keys.IS_QUAL_ACTIVE: rank['isQualActive']}

        if stats:
            arena.updateGameModeSpecificStats(isStatic=True, stats=stats)

    def __updateBannedVehicles(self):
        vehicleBanCtrl = self.__sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.COMP7_VEHICLE_BAN_CTRL)
        if vehicleBanCtrl is not None and self.bannedVehicles:
            vehicleBanCtrl.bannedVehicles = self.bannedVehicles
        return

    def __updateVehicleBanList(self):
        vehicleBanCtrl = self.__sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.COMP7_VEHICLE_BAN_CTRL)
        if vehicleBanCtrl is not None:
            vehicleBanCtrl.vehiclesListForBan = self.vehicleBanList
        return
