# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/plugins.py
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import VehicleMarkerPlugin
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
_EPIC_STATUS_EFFECTS_PRIORITY = (BATTLE_MARKER_STATES.STUN_STATE,
 BATTLE_MARKER_STATES.FL_REGENERATION_KIT_STATE,
 BATTLE_MARKER_STATES.REPAIRING_STATE,
 BATTLE_MARKER_STATES.ENGINEER_STATE,
 BATTLE_MARKER_STATES.HEALING_STATE,
 BATTLE_MARKER_STATES.BERSERKER_STATE,
 BATTLE_MARKER_STATES.STEALTH_STATE,
 BATTLE_MARKER_STATES.INSPIRING_STATE,
 BATTLE_MARKER_STATES.DEBUFF_STATE,
 BATTLE_MARKER_STATES.INSPIRED_STATE)

class EpicVehicleMarkerPlugin(VehicleMarkerPlugin):

    def _getMarkerStatusPriority(self, statusID):
        try:
            return _EPIC_STATUS_EFFECTS_PRIORITY.index(statusID)
        except ValueError:
            return -1


class EpicRespawnableVehicleMarkerPlugin(EpicVehicleMarkerPlugin):

    def start(self):
        super(EpicRespawnableVehicleMarkerPlugin, self).start()
        self._isSquadIndicatorEnabled = False

    def _hideVehicleMarker(self, vehicleID):
        self._destroyVehicleMarker(vehicleID)
