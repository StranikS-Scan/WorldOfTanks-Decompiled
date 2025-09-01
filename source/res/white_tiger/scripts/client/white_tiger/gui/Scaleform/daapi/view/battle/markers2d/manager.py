# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/markers2d/manager.py
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from white_tiger.gui.Scaleform.daapi.view.battle.markers2d.plugins import WhiteTigerBaseAreaMarkerPlugin, WhiteTigerVehicleMarkerPlugin

class WhiteTigerMarkersManager(MarkersManager):
    MARKERS_MANAGER_SWF = 'white_tiger|whiteTigerBattleMarkersApp.swf'

    def _setupPlugins(self, arenaVisitor):
        setup = super(WhiteTigerMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['area_markers'] = WhiteTigerBaseAreaMarkerPlugin
        setup['vehicles'] = WhiteTigerVehicleMarkerPlugin
        return setup
