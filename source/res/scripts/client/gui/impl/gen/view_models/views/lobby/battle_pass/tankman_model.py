# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tankman_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class TankmanStates(Enum):
    RECEIVED = 'received'
    AVAILABLEINPROGRESSION = 'availableInProgression'
    AVAILABLEINSHOP = 'availableInShop'
    UNAVAILABLE = 'unavailable'


class TankmanModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(TankmanModel, self).__init__(properties=properties, commands=commands)

    def getFullName(self):
        return self._getString(0)

    def setFullName(self, value):
        self._setString(0, value)

    def getGroupName(self):
        return self._getString(1)

    def setGroupName(self, value):
        self._setString(1, value)

    def getState(self):
        return TankmanStates(self._getString(2))

    def setState(self, value):
        self._setString(2, value.value)

    def getProgressionLevel(self):
        return self._getNumber(3)

    def setProgressionLevel(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(TankmanModel, self)._initialize()
        self._addStringProperty('fullName', '')
        self._addStringProperty('groupName', '')
        self._addStringProperty('state')
        self._addNumberProperty('progressionLevel', 0)
