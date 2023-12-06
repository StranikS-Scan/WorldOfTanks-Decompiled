# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_entry_point_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class State(Enum):
    BEFOREPROGRESSION = 'beforeProgression'
    ACTIVE = 'active'
    POSTPROGRESSION = 'postProgression'
    COMPLETED = 'completed'
    DISABLED = 'disabled'


class ArmoryYardEntryPointViewModel(ViewModel):
    __slots__ = ('onAction',)

    def __init__(self, properties=3, commands=1):
        super(ArmoryYardEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getProgressionLevel(self):
        return self._getNumber(1)

    def setProgressionLevel(self, value):
        self._setNumber(1, value)

    def getEndTimestamp(self):
        return self._getNumber(2)

    def setEndTimestamp(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(ArmoryYardEntryPointViewModel, self)._initialize()
        self._addStringProperty('state')
        self._addNumberProperty('progressionLevel', 0)
        self._addNumberProperty('endTimestamp', 0)
        self.onAction = self._addCommand('onAction')
