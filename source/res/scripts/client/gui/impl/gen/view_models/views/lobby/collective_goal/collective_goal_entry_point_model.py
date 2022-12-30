# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/collective_goal/collective_goal_entry_point_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class EventState(Enum):
    ACTIVE = 'active'
    FORBIDDEN = 'forbidden'
    NOTSTARTED = 'notStarted'
    FINISHED = 'finished'


class CollectiveGoalEntryPointModel(ViewModel):
    __slots__ = ('showProgression',)

    def __init__(self, properties=6, commands=1):
        super(CollectiveGoalEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getProgress(self):
        return self._getNumber(0)

    def setProgress(self, value):
        self._setNumber(0, value)

    def getCurrentGoal(self):
        return self._getNumber(1)

    def setCurrentGoal(self, value):
        self._setNumber(1, value)

    def getEventState(self):
        return EventState(self._getString(2))

    def setEventState(self, value):
        self._setString(2, value.value)

    def getPrevProgress(self):
        return self._getNumber(3)

    def setPrevProgress(self, value):
        self._setNumber(3, value)

    def getPrevEventState(self):
        return EventState(self._getString(4))

    def setPrevEventState(self, value):
        self._setString(4, value.value)

    def getStartDate(self):
        return self._getNumber(5)

    def setStartDate(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(CollectiveGoalEntryPointModel, self)._initialize()
        self._addNumberProperty('progress', 0)
        self._addNumberProperty('currentGoal', 0)
        self._addStringProperty('eventState')
        self._addNumberProperty('prevProgress', 0)
        self._addStringProperty('prevEventState')
        self._addNumberProperty('startDate', 0)
        self.showProgression = self._addCommand('showProgression')
