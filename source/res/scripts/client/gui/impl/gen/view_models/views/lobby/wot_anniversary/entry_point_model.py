# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/entry_point_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class State(Enum):
    AVAILABLE = 'available'
    IDLE = 'idle'
    COMPLETED = 'completed'


class EntryPointModel(ViewModel):
    __slots__ = ('onEnterEventLobby',)

    def __init__(self, properties=2, commands=1):
        super(EntryPointModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getEnvelopesCount(self):
        return self._getNumber(1)

    def setEnvelopesCount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(EntryPointModel, self)._initialize()
        self._addStringProperty('state', State.IDLE.value)
        self._addNumberProperty('envelopesCount', 0)
        self.onEnterEventLobby = self._addCommand('onEnterEventLobby')
