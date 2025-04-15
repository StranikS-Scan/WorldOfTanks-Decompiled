# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/markers2d/vehicle_plugins.py
from account_helpers.settings_core.settings_constants import MARKERS
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import SettingsPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from fall_tanks.gui.battle_control.arena_info.arena_vos import FallTanksKeys
from fall_tanks.gui.fall_tanks_gui_constants import FALL_TANKS_GUI_PROPS_NAME
_MARKER_SETTINGS = (('markerBaseIcon', False),
 ('markerBaseLevel', False),
 ('markerBaseHpIndicator', False),
 ('markerBaseDamage', False),
 ('markerBaseHp', 3),
 ('markerBaseVehicleName', True),
 ('markerBasePlayerName', True),
 ('markerAltIcon', False),
 ('markerAltLevel', False),
 ('markerAltHpIndicator', False),
 ('markerAltDamage', False),
 ('markerAltHp', 3),
 ('markerAltVehicleName', True),
 ('markerAltPlayerName', True))

class FallTanksSettingsPlugin(SettingsPlugin):
    __OVERRIDES = {MARKERS.ALLY: _MARKER_SETTINGS,
     MARKERS.ENEMY: _MARKER_SETTINGS,
     MARKERS.DEAD: _MARKER_SETTINGS}

    def __init__(self, parentObj):
        super(FallTanksSettingsPlugin, self).__init__(parentObj)
        self._overrides = self.__OVERRIDES


class FallTanksVehicleMarkerPlugin(RespawnableVehicleMarkerPlugin):
    __VEHICLE_MARKER_LINKAGE = 'FallTanksVehicleMarkerUI'

    def invalidateVehiclesStats(self, arenaDP):
        for vStats in (vStats for vStats in arenaDP.getVehiclesStatsIterator() if vStats.vehicleID in self._markers):
            self.__updatePlayerPosition(self._markers[vStats.vehicleID], vStats)

    def updateVehiclesStats(self, updated, arenaDP):
        for vStats in (vStats for _, vStats in updated if vStats.vehicleID in self._markers):
            self.__updatePlayerPosition(self._markers[vStats.vehicleID], vStats)

    @classmethod
    def _needsMarker(cls, vInfo):
        vehicleID = vInfo.vehicleID
        vStats = cls.sessionProvider.getArenaDP().getVehicleStats(vehicleID)
        isLeaver = vStats.gameModeSpecific.getValue(FallTanksKeys.IS_LEAVER)
        return super(cls, FallTanksVehicleMarkerPlugin)._needsMarker(vInfo) and not isLeaver

    def _getMarkerSymbol(self, vehicleID):
        return self.__VEHICLE_MARKER_LINKAGE

    def _getGuiPropsName(self, vInfo, guiProps):
        return FALL_TANKS_GUI_PROPS_NAME

    def _setVehicleInfo(self, marker, vInfo, guiProps, nameParts):
        super(FallTanksVehicleMarkerPlugin, self)._setVehicleInfo(marker, vInfo, guiProps, nameParts)
        vStats = self.sessionProvider.getArenaDP().getVehicleStats(vInfo.vehicleID)
        self.__updatePlayerPosition(marker, vStats)

    def __updatePlayerPosition(self, marker, vStats):
        position = vStats.gameModeSpecific.getValue(FallTanksKeys.RACE_POSITION)
        self._invokeMarker(marker.getMarkerID(), 'setPlayerPosition', position)
