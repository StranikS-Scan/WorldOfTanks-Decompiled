# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/portal_markers_manager.py
from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import MarkersManager
from portal.gui.Scaleform.daapi.view.battle.portal_vehicle_marker_plugins import PortalVehicleMarkerPlugin
from portal.gui.Scaleform.daapi.view.battle.shared.markers.markers2d import Portal2DAreaMarkersPlugin, PortalControlPointsPlugin

class PortalMarkersManager(MarkersManager):
    MARKERS_MANAGER_SWF = 'portal|portalBattleVehicleMarkersApp.swf'

    def _setupPlugins(self, arenaVisitor):
        setup = super(PortalMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = PortalVehicleMarkerPlugin
        setup['portal_2d_markers'] = Portal2DAreaMarkersPlugin
        setup['teamAndControlPoints'] = PortalControlPointsPlugin
        return setup
