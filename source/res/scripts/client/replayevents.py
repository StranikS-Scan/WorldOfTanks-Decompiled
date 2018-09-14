# Embedded file name: scripts/client/ReplayEvents.py
import Event

class _ReplayEvents(object):

    def __init__(self):
        self.onTimeWarpStart = Event.Event()
        self.onTimeWarpFinish = Event.Event()
        self.onPause = Event.Event()
        self.onMuteSound = Event.Event()


g_replayEvents = _ReplayEvents()
