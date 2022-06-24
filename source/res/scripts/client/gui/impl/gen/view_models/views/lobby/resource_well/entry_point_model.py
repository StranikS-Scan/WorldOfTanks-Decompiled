# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/resource_well/entry_point_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class EventState(IntEnum):
    ACTIVE = 0
    FORBIDDEN = 1
    PAUSED = 2
    COMPLETED = 3


class EntryPointModel(ViewModel):
    __slots__ = ('showProgression',)

    def __init__(self, properties=4, commands=1):
        super(EntryPointModel, self).__init__(properties=properties, commands=commands)

    def getProgress(self):
        return self._getNumber(0)

    def setProgress(self, value):
        self._setNumber(0, value)

    def getEventState(self):
        return EventState(self._getNumber(1))

    def setEventState(self, value):
        self._setNumber(1, value.value)

    def getPrevProgress(self):
        return self._getNumber(2)

    def setPrevProgress(self, value):
        self._setNumber(2, value)

    def getPrevEventState(self):
        return EventState(self._getNumber(3))

    def setPrevEventState(self, value):
        self._setNumber(3, value.value)

    def _initialize(self):
        super(EntryPointModel, self)._initialize()
        self._addNumberProperty('progress', 0)
        self._addNumberProperty('eventState')
        self._addNumberProperty('prevProgress', 0)
        self._addNumberProperty('prevEventState')
        self.showProgression = self._addCommand('showProgression')
