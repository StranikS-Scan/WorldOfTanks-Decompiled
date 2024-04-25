# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/MapImageComponent.py
import BigWorld
import Event

class MapImageComponent(BigWorld.DynamicScriptComponent):
    onMapUpdate = Event.Event()

    def __init__(self):
        super(MapImageComponent, self).__init__()
        self.onMapUpdate()

    def set_mapImage(self, prev):
        self.onMapUpdate()
