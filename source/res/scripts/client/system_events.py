# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/system_events.py
from __future__ import absolute_import
from events_container import EventsContainer

class SystemEvents(EventsContainer):

    def __init__(self):
        super(SystemEvents, self).__init__()
        self.onBeforeSend = self._createEvent()
        self.onDependencyConfigReady = self._createEvent()
        self.onFestivityConfigReady = self._createEvent()


g_systemEvents = SystemEvents()
