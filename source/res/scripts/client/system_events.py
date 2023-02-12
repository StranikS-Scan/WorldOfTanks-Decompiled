# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/system_events.py
from entity_events import EntityEvents

class SystemEvents(EntityEvents):

    def __init__(self):
        super(SystemEvents, self).__init__()
        self.onBeforeSend = self._createEvent()
        self.onDependencyConfigReady = self._createEvent()


g_systemEvents = SystemEvents()
