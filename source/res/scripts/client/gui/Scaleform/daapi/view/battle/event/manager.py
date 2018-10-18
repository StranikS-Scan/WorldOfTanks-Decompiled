# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/manager.py
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from gui.Scaleform.daapi.view.battle.event import plugins
from event_mode.event_ui import EventStaticObjectsPlugin

class PveMarkersManager(MarkersManager):

    def _setupPlugins(self, arenaVisitor):
        setup = super(PveMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = plugins.PveEventVehicleMarkerPlugin
        setup['eventMode'] = EventStaticObjectsPlugin
        return setup
