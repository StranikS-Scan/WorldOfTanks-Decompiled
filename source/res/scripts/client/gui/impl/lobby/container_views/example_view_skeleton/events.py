# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/container_views/example_view_skeleton/events.py
from gui.impl.lobby.container_views.base.events import ComponentEventsBase

class ExampleComponentViewEvents(ComponentEventsBase):

    def __init__(self):
        super(ExampleComponentViewEvents, self).__init__()
        self.onSelected = self._createEvent()
        self.onSomethingElse = self._createEvent()
