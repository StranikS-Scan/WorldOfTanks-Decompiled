# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/manager.py
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.plugins import WhiteTigerVehicleMarkerPlugin
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.plugins import WhiteTigerEventBusPlugin
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.plugins import WhiteTigerBaseAreaMarkerPlugin

class WhiteTigerMarkersManager(MarkersManager):
    MARKERS_MANAGER_SWF = 'white_tiger|white_tiger_battle_vehicle_markers.swf'

    def _setupPlugins(self, arenaVisitor):
        setup = super(WhiteTigerMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = WhiteTigerVehicleMarkerPlugin
        setup['eventBus'] = WhiteTigerEventBusPlugin
        setup['area_markers'] = WhiteTigerBaseAreaMarkerPlugin
        return setup
