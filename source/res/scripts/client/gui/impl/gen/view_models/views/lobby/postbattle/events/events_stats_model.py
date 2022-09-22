# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/events/events_stats_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.postbattle.events.base_event_model import BaseEventModel

class EventsStatsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(EventsStatsModel, self).__init__(properties=properties, commands=commands)

    def getEvents(self):
        return self._getArray(0)

    def setEvents(self, value):
        self._setArray(0, value)

    @staticmethod
    def getEventsType():
        return BaseEventModel

    def _initialize(self):
        super(EventsStatsModel, self)._initialize()
        self._addArrayProperty('events', Array())
