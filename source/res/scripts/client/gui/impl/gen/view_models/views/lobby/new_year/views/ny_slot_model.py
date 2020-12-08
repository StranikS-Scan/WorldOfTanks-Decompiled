# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_slot_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_with_roman_numbers_model import NyWithRomanNumbersModel

class NySlotModel(NyWithRomanNumbersModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(NySlotModel, self).__init__(properties=properties, commands=commands)

    def getSlotId(self):
        return self._getNumber(1)

    def setSlotId(self, value):
        self._setNumber(1, value)

    def getIcon(self):
        return self._getResource(2)

    def setIcon(self, value):
        self._setResource(2, value)

    def getType(self):
        return self._getString(3)

    def setType(self, value):
        self._setString(3, value)

    def getRank(self):
        return self._getNumber(4)

    def setRank(self, value):
        self._setNumber(4, value)

    def getIsBetterAvailable(self):
        return self._getBool(5)

    def setIsBetterAvailable(self, value):
        self._setBool(5, value)

    def getIsMaxLevel(self):
        return self._getBool(6)

    def setIsMaxLevel(self, value):
        self._setBool(6, value)

    def getIsMega(self):
        return self._getBool(7)

    def setIsMega(self, value):
        self._setBool(7, value)

    def getIsEmpty(self):
        return self._getBool(8)

    def setIsEmpty(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(NySlotModel, self)._initialize()
        self._addNumberProperty('slotId', 0)
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('type', '')
        self._addNumberProperty('rank', 0)
        self._addBoolProperty('isBetterAvailable', False)
        self._addBoolProperty('isMaxLevel', False)
        self._addBoolProperty('isMega', False)
        self._addBoolProperty('isEmpty', True)
