# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/events/events_stats_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.postbattle.events.base_event_model import BaseEventModel

class EventsStatsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(EventsStatsModel, self).__init__(properties=properties, commands=commands)

    def getEvents(self):
        return self._getArray(0)

    def setEvents(self, value):
        self._setArray(0, value)

    @staticmethod
    def getEventsType():
        return BaseEventModel

    def getHasQuestsToShow(self):
        return self._getBool(1)

    def setHasQuestsToShow(self, value):
        self._setBool(1, value)

    def getQuestsUpdateTimeLeft(self):
        return self._getNumber(2)

    def setQuestsUpdateTimeLeft(self, value):
        self._setNumber(2, value)

    def getIsHunter(self):
        return self._getBool(3)

    def setIsHunter(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(EventsStatsModel, self)._initialize()
        self._addArrayProperty('events', Array())
        self._addBoolProperty('hasQuestsToShow', True)
        self._addNumberProperty('questsUpdateTimeLeft', 0)
        self._addBoolProperty('isHunter', True)
