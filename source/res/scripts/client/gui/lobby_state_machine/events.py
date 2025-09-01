# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lobby_state_machine/events.py
from __future__ import absolute_import
from gui.shared.event_bus import SharedEvent
from gui.shared.events import NavigationEvent

class _BackNavigationEvent(SharedEvent):
    EVENT_ID = 'backNavigationEvent'

    def __init__(self, requestingState=None):
        super(_BackNavigationEvent, self).__init__(eventType=self.EVENT_ID)
        self.requestingState = requestingState


class _BackNavigationGeneratedNavigationEvent(NavigationEvent):

    def __init__(self, targetStateID, params, shouldKillView):
        super(_BackNavigationGeneratedNavigationEvent, self).__init__(targetStateID, params)
        self.shouldKillView = shouldKillView


class _NonViewClosingBackNavigationEvent(_BackNavigationEvent):
    EVENT_ID = 'nonViewClosingBackNavigationEvent'


class _StopEvent(NavigationEvent):
    pass
