# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/glade/slot_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class SlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
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

    def getType(self):
        return self._getString(3)

    def setType(self, value):
        self._setString(3, value)

    def getIsBetterAvailable(self):
        return self._getBool(4)

    def setIsBetterAvailable(self, value):
        self._setBool(4, value)

    def getIsMega(self):
        return self._getBool(5)

    def setIsMega(self, value):
        self._setBool(5, value)

    def getIsEmpty(self):
        return self._getBool(6)

    def setIsEmpty(self, value):
        self._setBool(6, value)

    def getIsPure(self):
        return self._getBool(7)

    def setIsPure(self, value):
        self._setBool(7, value)

    def getHasToyHint(self):
        return self._getBool(8)

    def setHasToyHint(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(SlotModel, self)._initialize()
        self._addNumberProperty('slotId', 0)
        self._addNumberProperty('toyId', 0)
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('type', '')
        self._addBoolProperty('isBetterAvailable', False)
        self._addBoolProperty('isMega', False)
        self._addBoolProperty('isEmpty', True)
        self._addBoolProperty('isPure', False)
        self._addBoolProperty('hasToyHint', False)
