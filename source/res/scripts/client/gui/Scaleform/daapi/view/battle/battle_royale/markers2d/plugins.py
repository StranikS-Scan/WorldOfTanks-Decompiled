# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/markers2d/plugins.py
from helpers import dependency
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import VehicleMarkerPlugin
from items.battle_royale import isSpawnedBot
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.battle_royale.markers2d import settings
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
_BATTLE_ROYALE_STATUS_EFFECTS_PRIORITY = (BATTLE_MARKER_STATES.STUN_STATE,
 BATTLE_MARKER_STATES.BERSERKER_STATE,
 BATTLE_MARKER_STATES.HEALING_STATE,
 BATTLE_MARKER_STATES.REPAIRING_STATE,
 BATTLE_MARKER_STATES.ENGINEER_STATE,
 BATTLE_MARKER_STATES.INSPIRING_STATE,
 BATTLE_MARKER_STATES.INSPIRED_STATE)

class RoyalBattleVehicleMarkerPlugin(VehicleMarkerPlugin):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def invalidateVehicleStatus(self, flags, vInfo, arenaDP):
        if not vInfo.isAlive() and isSpawnedBot(vInfo.vehicleType.tags):
            self._hideVehicleMarker(vInfo.vehicleID)

    def updateVehiclesInfo(self, updated, arenaDP):
        super(RoyalBattleVehicleMarkerPlugin, self).updateVehiclesInfo(updated, arenaDP)
        for _, vInfo in updated:
            if not vInfo.isAlive() and isSpawnedBot(vInfo.vehicleType.tags):
                self._hideVehicleMarker(vInfo.vehicleID)

    def _getMarkerSymbol(self, vehicleID):
        vehicleArenaInfoVO = self.__sessionProvider.getArenaDP().getVehicleInfo(vehicleID)
        return settings.BRmarkersSymbolsNames.BRANDER_BOT_SYMBOL if isSpawnedBot(vehicleArenaInfoVO.vehicleType.tags) else super(RoyalBattleVehicleMarkerPlugin, self)._getMarkerSymbol(vehicleID)

    def _getMarkerStatusPriority(self, statusID):
        try:
            return _BATTLE_ROYALE_STATUS_EFFECTS_PRIORITY.index(statusID)
        except ValueError:
            return -1
