# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/manager.py
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from gui.Scaleform.daapi.view.battle.event.plugins import EventVehicleMarkerPlugin
from gui.Scaleform.daapi.view.battle.event.plugins import EventEventBusPlugin

class EventMarkersManager(MarkersManager):

    def _setupPlugins(self, arenaVisitor):
        setup = super(EventMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = EventVehicleMarkerPlugin
        setup['eventBus'] = EventEventBusPlugin
        return setup
