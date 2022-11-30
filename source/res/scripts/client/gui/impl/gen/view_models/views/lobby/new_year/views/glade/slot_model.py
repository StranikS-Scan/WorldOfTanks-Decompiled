# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/glade/slot_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class SlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(SlotModel, self).__init__(properties=properties, commands=commands)

    def getSlotId(self):
        return self._getNumber(0)

    def setSlotId(self, value):
        self._setNumber(0, value)

    def getToyId(self):
        return self._getNumber(1)

    def setToyId(self, value):
        self._setNumber(1, value)

    def getIcon(self):
        return self._getResource(2)

    def setIcon(self, value):
        self._setResource(2, value)

    def getIsNew(self):
        return self._getBool(3)

    def setIsNew(self, value):
        self._setBool(3, value)

    def getIsEmpty(self):
        return self._getBool(4)

    def setIsEmpty(self, value):
        self._setBool(4, value)

    def getNewToys(self):
        return self._getArray(5)

    def setNewToys(self, value):
        self._setArray(5, value)

    @staticmethod
    def getNewToysType():
        return str

    def _initialize(self):
        super(SlotModel, self)._initialize()
        self._addNumberProperty('slotId', 0)
        self._addNumberProperty('toyId', 0)
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('isNew', False)
        self._addBoolProperty('isEmpty', True)
        self._addArrayProperty('newToys', Array())
