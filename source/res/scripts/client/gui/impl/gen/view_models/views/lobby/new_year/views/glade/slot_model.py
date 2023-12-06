# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/glade/slot_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class SlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(SlotModel, self).__init__(properties=properties, commands=commands)

    def getSlotId(self):
        return self._getNumber(0)

    def setSlotId(self, value):
        self._setNumber(0, value)

    def getToyId(self):
        return self._getNumber(1)

    def setToyId(self, value):
        self._setNumber(1, value)

    def getRank(self):
        return self._getNumber(2)

    def setRank(self, value):
        self._setNumber(2, value)

    def getIcon(self):
        return self._getResource(3)

    def setIcon(self, value):
        self._setResource(3, value)

    def getType(self):
        return self._getString(4)

    def setType(self, value):
        self._setString(4, value)

    def getIsBetterAvailable(self):
        return self._getBool(5)

    def setIsBetterAvailable(self, value):
        self._setBool(5, value)

    def getIsEmpty(self):
        return self._getBool(6)

    def setIsEmpty(self, value):
        self._setBool(6, value)

    def getHasToyHint(self):
        return self._getBool(7)

    def setHasToyHint(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(SlotModel, self)._initialize()
        self._addNumberProperty('slotId', 0)
        self._addNumberProperty('toyId', 0)
        self._addNumberProperty('rank', 0)
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('type', '')
        self._addBoolProperty('isBetterAvailable', False)
        self._addBoolProperty('isEmpty', True)
        self._addBoolProperty('hasToyHint', False)
