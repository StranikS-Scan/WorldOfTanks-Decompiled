# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/manager.py
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from gui.Scaleform.daapi.view.battle.event.plugins import EventVehicleMarkerPlugin
from gui.Scaleform.daapi.view.battle.event.world_markers_controllers import WorldMarkersPlugin
from gui.Scaleform.daapi.view.battle.event.marker_gui_provider import EventAreaPointMarkerPlugin, EventDeathZonesMarkersPlugin
from soft_exception import SoftException
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings

class EventMarkersManager(MarkersManager):
    _DEF_MARKER_SETTINGS = (40.0, 100.0, 95.0, 3.0)

    def createMarker(self, symbol, matrixProvider=None, active=True):
        if active and matrixProvider is None:
            raise SoftException('Active marker {} must has matrixProvider'.format(symbol))
        scalable = False if symbol == settings.MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER else True
        markerID = self.canvas.addMarker(matrixProvider, symbol, active, scalable)
        self.ids.add(markerID)
        return markerID

    def getGUIMarkerSettings(self):
        return self._DEF_MARKER_SETTINGS

    def _setupPlugins(self, arenaVisitor):
        setup = super(EventMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = EventVehicleMarkerPlugin
        setup['event_markers'] = WorldMarkersPlugin
        setup['area_point_marker'] = EventAreaPointMarkerPlugin
        setup['deathzones_markers'] = EventDeathZonesMarkersPlugin
        return setup
