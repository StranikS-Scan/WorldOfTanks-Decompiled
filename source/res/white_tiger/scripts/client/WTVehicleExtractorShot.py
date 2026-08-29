# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleExtractorShot.py
import BigWorld
from helpers import dependency
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import EventKeys
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from skeletons.gui.battle_session import IBattleSessionProvider
from script_component.DynamicScriptComponent import DynamicScriptComponent
from white_tiger.gui.battle_control.controllers.consumables.equipment_sound import playExtractorShot

class WTVehicleExtractorShot(DynamicScriptComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WTVehicleExtractorShot, self).__init__()
        self.__updatePlasmaMarker()

    def set_plasmaCounter(self, _):
        self.__updatePlasmaMarker()
        self.__updatePlayerPlugin()

    def set_isShotFiring(self, prev):
        if self.isShotFiring:
            isPC = self.entity.id == BigWorld.player().playerVehicleID
            playExtractorShot(isPC, self.entity.position)

    def onLeaveWorld(self):
        arena = avatar_getter.getArena()
        if arena is not None:
            arena.onNewVehicleListReceived -= self.__onNewVehicleListReceived
            arena.onVehicleAdded -= self.__onVehicleAdded
        super(WTVehicleExtractorShot, self).onLeaveWorld()
        return

    def _onAvatarReady(self):
        arena = avatar_getter.getArena()
        if arena is not None:
            arena.onNewVehicleListReceived += self.__onNewVehicleListReceived
            arena.onVehicleAdded += self.__onVehicleAdded
        self.__updatePlasmaMarker()
        return

    def __onNewVehicleListReceived(self):
        self.__updatePlasmaMarker()

    def __onVehicleAdded(self, vehicleID):
        if self._isAvatarReady and vehicleID == self.entity.id:
            self.__updatePlasmaMarker()

    def __updatePlasmaMarker(self):
        vInfos = self.__sessionProvider.getArenaDP().getVehiclesInfoIterator()
        if self.entity.id not in [ vInfo.vehicleID for vInfo in vInfos ]:
            return
        arena = avatar_getter.getArena()
        gameModeStats = {}
        gameModeStats[self.entity.id] = {EventKeys.PLASMA_COUNT.value: self.plasmaCounter}
        arena.onGameModeSpecificStats(True, gameModeStats)

    def __updatePlayerPlugin(self):
        ctrl = self.entity.guiSessionProvider.shared.vehicleState
        totalPlasmaBonus = self.plasmaCounter * self.multiplierDamagePerPlasma + 1
        ctrl.notifyStateChanged(VEHICLE_VIEW_STATE.PLASMA, (self.plasmaCounter, totalPlasmaBonus, 0))
