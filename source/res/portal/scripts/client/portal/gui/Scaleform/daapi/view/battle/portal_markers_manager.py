# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/portal_markers_manager.py
from account_helpers.settings_core.settings_constants import MARKERS
from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import MarkersManager
from portal.gui.Scaleform.daapi.view.battle.portal_vehicle_marker_plugins import PortalVehicleMarkerPlugin
from portal.gui.Scaleform.daapi.view.battle.shared.markers.markers2d import Portal2DAreaMarkersPlugin, PortalControlPointsPlugin

class PortalMarkersManager(MarkersManager):
    MARKERS_MANAGER_SWF = 'portal|portalBattleVehicleMarkersApp.swf'
    PORTAL_MARKER_SETTINGS = {MARKERS.ENEMY: {'markerBaseVehicleName': 1,
                     'markerAltVehicleName': 1,
                     'markerBasePlayerName': 0,
                     'markerAltPlayerName': 0,
                     'markerBaseHpIndicator': 1,
                     'markerAltHpIndicator': 1,
                     'markerBaseDamage': 1,
                     'markerAltDamage': 1,
                     'markerBaseIcon': 1,
                     'markerAltIcon': 1,
                     'markerBaseAimMarker2D': 0,
                     'markerAltAimMarker2D': 0,
                     'markerBaseVehicleDist': 0,
                     'markerAltVehicleDist': 0,
                     'markerBaseLevel': 0,
                     'markerAltLevel': 0},
     MARKERS.DEAD: {'markerBaseVehicleName': 1,
                    'markerAltVehicleName': 1,
                    'markerBasePlayerName': 1,
                    'markerAltPlayerName': 1,
                    'markerBaseHpIndicator': 0,
                    'markerAltHpIndicator': 0,
                    'markerBaseDamage': 0,
                    'markerAltDamage': 0,
                    'markerBaseIcon': 1,
                    'markerAltIcon': 1,
                    'markerBaseAimMarker2D': 0,
                    'markerAltAimMarker2D': 0,
                    'markerBaseVehicleDist': 0,
                    'markerAltVehicleDist': 0,
                    'markerBaseLevel': 0,
                    'markerAltLevel': 0,
                    'markerBaseHp': 3,
                    'markerAltHp': 3},
     MARKERS.ALLY: {'markerBaseVehicleName': 1,
                    'markerAltVehicleName': 1,
                    'markerBasePlayerName': 1,
                    'markerAltPlayerName': 1,
                    'markerBaseHpIndicator': 1,
                    'markerAltHpIndicator': 1,
                    'markerBaseDamage': 1,
                    'markerAltDamage': 1,
                    'markerBaseIcon': 1,
                    'markerAltIcon': 1,
                    'markerBaseAimMarker2D': 0,
                    'markerAltAimMarker2D': 0,
                    'markerBaseVehicleDist': 0,
                    'markerAltVehicleDist': 0,
                    'markerBaseLevel': 0,
                    'markerAltLevel': 0}}

    def _setupPlugins(self, arenaVisitor):
        setup = super(PortalMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = PortalVehicleMarkerPlugin
        setup['portal_2d_markers'] = Portal2DAreaMarkersPlugin
        setup['teamAndControlPoints'] = PortalControlPointsPlugin
        return setup

    def setMarkerSettings(self, markerSettings, notify=False):
        portalMarkerSettings = self.PORTAL_MARKER_SETTINGS.copy()
        portalMarkerSettings[MARKERS.ENEMY]['markerBaseHp'] = markerSettings[MARKERS.ENEMY]['markerBaseHp']
        portalMarkerSettings[MARKERS.ENEMY]['markerAltHp'] = markerSettings[MARKERS.ENEMY]['markerAltHp']
        portalMarkerSettings[MARKERS.ALLY]['markerBaseHp'] = markerSettings[MARKERS.ALLY]['markerBaseHp']
        portalMarkerSettings[MARKERS.ALLY]['markerAltHp'] = markerSettings[MARKERS.ALLY]['markerAltHp']
        super(PortalMarkersManager, self).setMarkerSettings(portalMarkerSettings, notify)
