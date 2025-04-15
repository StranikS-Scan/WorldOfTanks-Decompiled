# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBAttackDirectionMarkerComponent.py
import BigWorld
import Event

class HBAttackDirectionMarkerComponent(BigWorld.DynamicScriptComponent):
    onMarkersUpdated = Event.Event()

    def set_markers(self, _):
        self.onMarkersUpdated(self.markers)
