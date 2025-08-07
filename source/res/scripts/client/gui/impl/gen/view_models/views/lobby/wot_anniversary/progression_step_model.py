# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/progression_step_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ProgressionState(Enum):
    RECEIVED = 'received'
    IN_PROGRESS = 'inProgress'
    LOCKED = 'locked'


class ProgressionStepModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ProgressionStepModel, self).__init__(properties=properties, commands=commands)

    def getRequired(self):
        return self._getNumber(0)

    def setRequired(self, value):
        self._setNumber(0, value)

    def getActual(self):
        return self._getNumber(1)

    def setActual(self, value):
        self._setNumber(1, value)

    def getState(self):
        return ProgressionState(self._getString(2))

    def setState(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(ProgressionStepModel, self)._initialize()
        self._addNumberProperty('required', 0)
        self._addNumberProperty('actual', 0)
        self._addStringProperty('state')
