# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/glade/toy_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class SlotState(Enum):
    UNAVAILABLE = 'unavailable'
    AVAILABLE = 'available'
    SELECTED = 'selected'
    DISABLED = 'disabled'


class ToyModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(ToyModel, self).__init__(properties=properties, commands=commands)

    def getToyID(self):
        return self._getNumber(0)

    def setToyID(self, value):
        self._setNumber(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getIsNew(self):
        return self._getBool(2)

    def setIsNew(self, value):
        self._setBool(2, value)

    def getPrice(self):
        return self._getNumber(3)

    def setPrice(self, value):
        self._setNumber(3, value)

    def getState(self):
        return SlotState(self._getString(4))

    def setState(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(ToyModel, self)._initialize()
        self._addNumberProperty('toyID', 0)
        self._addStringProperty('icon', '')
        self._addBoolProperty('isNew', False)
        self._addNumberProperty('price', 0)
        self._addStringProperty('state')
