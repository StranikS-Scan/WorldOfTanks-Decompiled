# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_slot_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NySlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(NySlotModel, self).__init__(properties=properties, commands=commands)

    def getSlotId(self):
        return self._getNumber(0)

    def setSlotId(self, value):
        self._setNumber(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getRankIcon(self):
        return self._getResource(2)

    def setRankIcon(self, value):
        self._setResource(2, value)

    def getIsBetterAvailable(self):
        return self._getBool(3)

    def setIsBetterAvailable(self, value):
        self._setBool(3, value)

    def getIsMaxLevel(self):
        return self._getBool(4)

    def setIsMaxLevel(self, value):
        self._setBool(4, value)

    def getIsMega(self):
        return self._getBool(5)

    def setIsMega(self, value):
        self._setBool(5, value)

    def getIsEmpty(self):
        return self._getBool(6)

    def setIsEmpty(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(NySlotModel, self)._initialize()
        self._addNumberProperty('slotId', 0)
        self._addResourceProperty('icon', R.invalid())
        self._addResourceProperty('rankIcon', R.invalid())
        self._addBoolProperty('isBetterAvailable', False)
        self._addBoolProperty('isMaxLevel', False)
        self._addBoolProperty('isMega', False)
        self._addBoolProperty('isEmpty', True)
