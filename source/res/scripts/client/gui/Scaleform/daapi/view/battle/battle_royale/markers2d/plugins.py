# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/markers2d/plugins.py
import logging
from account_helpers.settings_core.settings_constants import MARKERS
from gui.Scaleform.daapi.view.battle.battle_royale.markers2d import settings
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import SettingsPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import VehicleMarkerPlugin
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from helpers import dependency
from items.battle_royale import isSpawnedBot
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)
_BATTLE_ROYALE_STATUS_EFFECTS_PRIORITY = (BATTLE_MARKER_STATES.STUN_STATE,
 BATTLE_MARKER_STATES.DEBUFF_STATE,
 BATTLE_MARKER_STATES.BERSERKER_STATE,
 BATTLE_MARKER_STATES.INSPIRING_STATE,
 BATTLE_MARKER_STATES.INSPIRED_STATE,
 BATTLE_MARKER_STATES.HEALING_STATE,
 BATTLE_MARKER_STATES.REPAIRING_STATE,
 BATTLE_MARKER_STATES.ENGINEER_STATE)

class BattleRoyaleVehicleMarkerPlugin(VehicleMarkerPlugin):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def invalidateVehicleStatus(self, flags, vInfo, arenaDP):
        if not vInfo.isAlive() and isSpawnedBot(vInfo.vehicleType.tags):
            self._hideVehicleMarker(vInfo.vehicleID)

    def updateVehiclesInfo(self, updated, arenaDP):
        super(BattleRoyaleVehicleMarkerPlugin, self).updateVehiclesInfo(updated, arenaDP)
        for _, vInfo in updated:
            if not vInfo.isAlive() and isSpawnedBot(vInfo.vehicleType.tags):
                self._hideVehicleMarker(vInfo.vehicleID)

    def _getMarkerSymbol(self, vehicleID):
        vehicleArenaInfoVO = self.__sessionProvider.getArenaDP().getVehicleInfo(vehicleID)
        return settings.BRmarkersSymbolsNames.BRANDER_BOT_SYMBOL if isSpawnedBot(vehicleArenaInfoVO.vehicleType.tags) else super(BattleRoyaleVehicleMarkerPlugin, self)._getMarkerSymbol(vehicleID)

    def _getMarkerStatusPriority(self, statusID):
        try:
            return _BATTLE_ROYALE_STATUS_EFFECTS_PRIORITY.index(statusID)
        except ValueError:
            return -1


class BattleRoyaleSettingsPlugin(SettingsPlugin):
    __CUSTOM = (('markerBaseLevel', 0), ('markerAltLevel', 0))

    def _setMarkerSettings(self, notify=False):
        getter = self.settingsCore.getSetting
        result = {}
        for name in MARKERS.ALL():
            stgs = getter(name)
            for custOptName, custOptVal in self.__CUSTOM:
                if custOptName not in stgs:
                    _logger.warning('Option "%s" is not in list of options', custOptName)
                stgs[custOptName] = custOptVal

            result[name] = stgs

        self._parentObj.setMarkerSettings(result, notify=notify)
